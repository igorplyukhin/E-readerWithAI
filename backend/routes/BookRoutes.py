import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import aiofiles
from fastapi.encoders import jsonable_encoder  # Важно: для преобразования ObjectId
from utils.BookProcessor import BookProcessor
from utils.Fb2Processor import Fb2Processor
from models.TextBlock import TextBlock
from models.BookDetailResponse import BookDetailResponse
from models.BookPageResponse import BookPageResponse


book_router = APIRouter()

# MongoDB setup
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["database"]
books_collection = db["books"]
text_blocks_collection = db["text_blocks"]
users_collection = db["users"]

class BookText(BaseModel):
    title: str
    authors: str
    content: str
    annotation: Optional[str]

class BookResponse(BaseModel):
    status: str
    message: str
    book: Optional[dict]

class Book(BaseModel):
    idBook: str
    title: str
    authors: str
    annotation: Optional[str]
    textBlockIds: List[str]

async def save_file(file: UploadFile, upload_dir: str, file_name: str) -> Optional[str]:
    file_path = os.path.join(upload_dir, file_name)
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

def get_supported_file_type(file_name: str) -> Optional[str]:
    extension = file_name.split('.')[-1].lower()
    return {
        "pdf": "application/pdf",
        "fb2": "application/fb2+xml",
        "txt": "text/plain"
    }.get(extension)

@book_router.post("/upload_book")
async def upload_book(
    background_tasks: BackgroundTasks,
    id: str = Form(...),
    file: UploadFile = File(...)
):
    file_name = file.filename if file.filename else "default.fb2"
    file_type = get_supported_file_type(file_name)
    
    if not file_type:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = await save_file(file, upload_dir, file_name)
    
    if not file_path:
        raise HTTPException(status_code=500, detail="Error saving file")
    
    # Читаем и обрабатываем файл
    try:
        if file_type == "application/pdf":
            book_processor = BookProcessor(file_path, file_name)
            book_text = book_processor.read_pdf_file()
        elif file_type == "application/fb2+xml":
            fb2_processor = Fb2Processor(file_path)
            book_text = fb2_processor.extract_book_text()
        elif file_type == "text/plain":
            book_processor = BookProcessor(file_path, file_name)
            book_text = book_processor.read_text_file()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    if not book_text:
        raise HTTPException(status_code=500, detail="Error processing file")
    
    # Получаем структуру книги и текстовые блоки
    try:
        book_processor = BookProcessor(file_path, file_name)
        book = book_processor.get_book(file_type)
        chapters = book_processor.get_chapters(file_type)
        text_blocks = book_processor.process_chapters_and_blocks(chapters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing book: {str(e)}")

    # Сериализуем книгу и вставляем в базу данных
    book_dict = jsonable_encoder(book)
    try:
        result = await books_collection.insert_one(book_dict)
        book_id = str(result.inserted_id)
        book_dict["_id"] = book_id  # Заменяем ObjectId на строку

        # Сериализуем и вставляем text_blocks
        text_block_documents = jsonable_encoder(text_blocks)
        result = await text_blocks_collection.insert_many(text_block_documents)
        text_block_ids = [str(obj_id) for obj_id in result.inserted_ids]

        # Обновляем книгу с textBlockIds
        await books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": {"textBlockIds": text_block_ids}}
        )

        # Обновляем пользователя
        await users_collection.update_one(
            {"_id": id},
            {"$addToSet": {"bookIds": book_id}, "$inc": {"countBook": 1}}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

    return JSONResponse(content={
        "status": "success", 
        "message": "Book uploaded and processed", 
        "book": book_dict
    })

@book_router.get("/get_book_detail")
async def get_book_detail(id: str = Query(..., description="ID книги")):
    if not id:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Не предоставлен ID книги"})

    try:
        object_id = ObjectId(id)
    except:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Неверный формат ID книги"})

    book_doc = await books_collection.find_one({"_id": object_id})
    if not book_doc:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Книга не найдена"})

    book = Book(
        idBook=str(book_doc["_id"]),
        title=book_doc.get("title", "Без названия"),
        authors=book_doc.get("author", "Неизвестно"),
        annotation=book_doc.get("annotation"),
        textBlockIds=book_doc.get("textBlockIds", [])
    )


    object_id_list = [ObjectId(tid) for tid in book.textBlockIds]

    text_block_docs = await text_blocks_collection.find({"_id": {"$in": object_id_list}}).to_list(length=None)

    text_blocks = []
    for doc in text_block_docs:
        text_block = TextBlock(
            _id=str(doc["_id"]),
            original=doc.get("original", ""),
            numberChapter=doc.get("numberChapter", 0),
            summary=doc.get("summary"),
            summaryTime=doc.get("summaryTime"),
            questions=doc.get("questions", []),
            rightAnswers=doc.get("rightAnswers", [])
        )
        text_blocks.append(text_block)

    response = BookDetailResponse(
        annotation=book.annotation or "",
        totalPages=len(text_blocks),
        textBlocks=[tb.original for tb in text_blocks]
    )

    return JSONResponse(status_code=200, content=response.dict())

@book_router.get("/get_book_page")
async def get_book_page(
    id: str = Query(..., description="ID книги"),
    page: int = Query(..., description="Номер страницы (начиная с 1)")
):
    if not id or page is None:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Не предоставлены ID книги или номер страницы"})

    if page < 1:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Неверный номер страницы"})

    try:
        object_id = ObjectId(id)
    except:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Неверный формат ID книги"})

    book_doc = await books_collection.find_one({"_id": object_id})
    if not book_doc:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Книга не найдена"})

    # Преобразуем документ в объект Book
    book = Book(
        idBook=str(book_doc["_id"]),
        title=book_doc.get("title", "Без названия"),
        authors=book_doc.get("author", "Неизвестно"),
        annotation=book_doc.get("annotation"),
        textBlockIds=book_doc.get("textBlockIds", [])
    )

    if page > len(book.textBlockIds):
        return JSONResponse(status_code=404, content={"status": "error", "message": "Страница не найдена"})

    text_block_id = book.textBlockIds[page - 1]

    try:
        block_object_id = ObjectId(text_block_id)
    except:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Неверный формат ID блока"})

    text_block_doc = await text_blocks_collection.find_one({"_id": block_object_id})
    if not text_block_doc:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Страница не найдена"})

    text_block = TextBlock(
        _id=str(text_block_doc["_id"]),
        original=text_block_doc.get("original", ""),
        numberChapter=text_block_doc.get("numberChapter", 0),
        summary=text_block_doc.get("summary"),
        summaryTime=text_block_doc.get("summaryTime"),
        questions=text_block_doc.get("questions", []),
        rightAnswers=text_block_doc.get("rightAnswers", [])
    )

    response = BookPageResponse(
        pageNumber=page,
        totalPages=len(book.textBlockIds),
        content=text_block.original
    )

    return JSONResponse(status_code=200, content=response.dict())
