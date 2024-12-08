import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.background import BackgroundTasks
import aiofiles

book_router = APIRouter()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["book_database"]
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

class BookDetailResponse(BaseModel):
    annotation: str
    totalPages: int
    textBlocks: List[str]

class BookPageResponse(BaseModel):
    pageNumber: int
    totalPages: int
    content: str

class Book(BaseModel):
    idBook: str
    title: str
    authors: str
    annotation: Optional[str]
    textBlockIds: List[str]

def is_supported_mime_type(mime_type: str) -> bool:
    return mime_type in ["application/pdf", "application/fb2+xml", "text/plain"]

def get_supported_file_type(file_type: str, file_name: str) -> Optional[str]:
    mime_types = {"application/pdf", "application/fb2+xml", "text/plain"}
    if file_type in mime_types:
        return file_type
    file_extension = file_name.split('.')[-1].lower()
    return {
        "pdf": "application/pdf",
        "fb2": "application/fb2+xml",
        "txt": "text/plain"
    }.get(file_extension)

async def save_file(file: UploadFile, upload_dir: str, file_name: str) -> Optional[str]:
    file_path = os.path.join(upload_dir, file_name)
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        return file_path
    except Exception as e:
        return None

@book_router.post("/upload_book")
async def upload_book(
    background_tasks: BackgroundTasks,
    id: str = Form(...),
    file: UploadFile = File(...)
):
    file_name = file.filename if file.filename else "default.fb2"
    file_type = get_supported_file_type(file.content_type, file_name)

    if not file_type:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = await save_file(file, upload_dir, file_name)
    if not file_path:
        raise HTTPException(status_code=500, detail="Error saving file")

    book_text = None
    if file_type == "application/pdf":
        # Process PDF file
        book_text = BookText(
            title="Unknown",
            authors="Unknown",
            content="PDF content",
            annotation=None
        )
    elif file_type == "application/fb2+xml":
        # Process FB2 file
        book_text = BookText(
            title="Unknown",
            authors="Unknown",
            content="FB2 content",
            annotation=None
        )
    elif file_type == "text/plain":
        # Process text file
        book_text = BookText(
            title="Unknown",
            authors="Unknown",
            content="Text content",
            annotation=None
        )

    if not book_text:
        raise HTTPException(status_code=500, detail="Error processing file")

    book = Book(
        idBook=str(ObjectId()),
        title=book_text.title,
        authors=book_text.authors,
        annotation=book_text.annotation,
        textBlockIds=[]
    )

    text_blocks = [{"original": book_text.content}]

    try:
        books_collection.insert_one(jsonable_encoder(book))
        text_blocks_collection.insert_many(jsonable_encoder(text_blocks))
        books_collection.update_one(
            {"_id": ObjectId(book.idBook)},
            {"$set": {"textBlockIds": [str(ObjectId())]}}
        )
        users_collection.update_one(
            {"_id": id},
            {"$addToSet": {"bookIds": book.idBook}, "$inc": {"countBook": 1}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

    return JSONResponse(content=jsonable_encoder(BookResponse(status="success", message="Book uploaded and processed", book=book)))

@book_router.post("/get_book")
async def get_book(id_book: str = Form(...)):
    book_doc = books_collection.find_one({"_id": ObjectId(id_book)})
    if not book_doc:
        raise HTTPException(status_code=404, detail="Book not found")
    book = Book(**book_doc)
    return JSONResponse(content=jsonable_encoder(book))

@book_router.post("/change_mode")
async def change_mode(id_book: str = Form(...), mode: str = Form(...)):
    book_doc = books_collection.find_one({"_id": ObjectId(id_book)})
    if not book_doc:
        raise HTTPException(status_code=404, detail="Book not found")

    if mode in ["summarization", "summarization_time"]:
        BackgroundTasks.add_task(process_summarization_mode, book_doc, mode)
        update_result = books_collection.update_one(
            {"_id": ObjectId(id_book)},
            {"$set": {"mode": mode}}
        )
        if update_result.matched_count > 0:
            return JSONResponse(content={"message": "Summarization mode set and processing started"})
        else:
            raise HTTPException(status_code=500, detail="Failed to change mode")
    elif mode == "questions_original_text":
        books_collection.update_one(
            {"_id": ObjectId(id_book)},
            {"$set": {"mode": mode}}
        )
        return JSONResponse(content={"message": "Questions mode set"})
    elif mode == "retelling":
        retelling = get_book_retelling(id_book)
        return JSONResponse(content={"retelling": retelling})
    elif mode == "test":
        test = generate_test_for_book(id_book)
        return JSONResponse(content=test)
    elif mode == "similar_books":
        recommendations = get_similar_books(id_book)
        return JSONResponse(content=recommendations)
    else:
        raise HTTPException(status_code=400, detail="Unknown mode")

@book_router.get("/get_book_detail")
async def get_book_detail(id: str = Query(...)):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid book ID format")

    book_doc = books_collection.find_one({"_id": object_id})
    if not book_doc:
        raise HTTPException(status_code=404, detail="Book not found")

    book = Book(**book_doc)
    text_block_docs = text_blocks_collection.find({"_id": {"$in": [ObjectId(tid) for tid in book.textBlockIds]}})
    text_blocks = [doc["original"] for doc in text_block_docs]

    response = BookDetailResponse(
        annotation=book.annotation if book.annotation else "",
        totalPages=len(text_blocks),
        textBlocks=text_blocks
    )
    return JSONResponse(content=jsonable_encoder(response))

@book_router.get("/get_book_page")
async def get_book_page(id: str = Query(...), page: int = Query(...)):
    if page < 1:
        raise HTTPException(status_code=400, detail="Invalid page number")

    book_doc = books_collection.find_one({"_id": ObjectId(id)})
    if not book_doc:
        raise HTTPException(status_code=404, detail="Book not found")

    book = Book(**book_doc)
    if page > len(book.textBlockIds):
        raise HTTPException(status_code=404, detail="Page not found")

    text_block_id = book.textBlockIds[page - 1]
    text_block_doc = text_blocks_collection.find_one({"_id": ObjectId(text_block_id)})
    if not text_block_doc:
        raise HTTPException(status_code=404, detail="Page not found")

    text_block = text_block_doc["original"]
    response = BookPageResponse(
        pageNumber=page,
        totalPages=len(book.textBlockIds),
        content=text_block
    )
    return JSONResponse(content=jsonable_encoder(response))

def process_summarization_mode(book_doc, mode):
    # Implement background processing for summarization mode
    pass

def get_book_retelling(id_book):
    # Implement retelling extraction
    return "Retelling content"

def generate_test_for_book(id_book):
    # Implement test generation
    return {"questions": ["Question 1", "Question 2"]}

def get_similar_books(id_book):
    # Implement similar books recommendation
    return ["Similar Book 1", "Similar Book 2"]

