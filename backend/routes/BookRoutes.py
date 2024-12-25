import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import aiofiles
from Services.BookService import BookService
from Services.GigaChatServices import get_author_info

book_router = APIRouter()
book_service = BookService()


class Book(BaseModel):
    idBook: str
    title: str
    authors: str
    annotation: Optional[str]
    textBlockIds: List[str]


@book_router.post(
    "/api/book/upload",
    summary="Загрузить новую книгу",
    description="",
    tags=["Загрузка и работа с файлами"],
)
async def upload_book(
    user_id: str = Query(..., description="Id пользователя"),
    file: UploadFile = File(..., description="Книга в формате PDF"),
):
    file_name = file.filename if file.filename else "default.fb2"
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = os.path.join(upload_dir, file_name)
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    if not file_path:
        raise HTTPException(status_code=500, detail="Error saving file")

    # Обработка загруженной книги
    book_dict = await book_service.process_uploaded_book(file_path, file_name, user_id)

    # Вызов функции для получения информации об авторе
    author_info = await get_author_info(
        book_dict["title"], book_dict["authors"], book_dict["annotation"] or ""
    )
    print(author_info)  # Здесь вы получите информацию об авторе

    return JSONResponse(
        content={
            "status": "success",
            "message": "Book uploaded and processed",
            "book": book_dict,
        }
    )


@book_router.get(
    "/api/book/detail",
    summary="Получить загруженную книгу",
    description="",
    tags=["Загрузка и работа с файлами"],
)
async def get_book_detail(id: str = Query(..., description="ID книги")):
    if not id:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Не предоставлен ID книги"},
        )

    try:
        # Получаем книгу по ID
        book_doc = await book_service.book_repository.get_book_by_id(id)
        if not book_doc:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Книга не найдена"},
            )

        # Получаем текстовые блоки по их ID
        text_block_ids = book_doc.get("textBlockIds", [])
        text_blocks = []
        for block_id in text_block_ids:
            text_block_doc = await book_service.book_repository.get_text_block_by_id(
                block_id
            )
            if text_block_doc:
                text_blocks.append(text_block_doc.get("original", ""))

        # Формируем ответ
        response = {
            "annotation": book_doc.get("annotation", ""),
            "totalPages": len(text_block_ids),
            "textBlocks": text_blocks,
        }

        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Ошибка при получении книги: {str(e)}",
            },
        )


@book_router.get(
    "/api/book/page",
    summary="Получить станицу щагруженной книги",
    description="",
    tags=["Загрузка и работа с файлами"],
)
async def get_book_page(
    id: str = Query(..., description="ID книги"),
    page: int = Query(1, description="Номер страницы (начиная с 1)"),
):
    if not id or page is None:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Не предоставлены ID книги или номер страницы",
            },
        )

    if page < 1:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Неверный номер страницы"},
        )

    try:
        book_doc = await book_service.book_repository.get_book_by_id(id)
        if not book_doc:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Книга не найдена"},
            )

        book = {
            "idBook": str(book_doc["_id"]),
            "title": book_doc.get("title", "Без названия"),
            "authors": book_doc.get("author", "Неизвестно"),
            "annotation": book_doc.get("annotation"),
            "textBlockIds": book_doc.get("textBlockIds", []),
        }

        if page > len(book["textBlockIds"]):
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Страница не найдена"},
            )

        text_block_id = book["textBlockIds"][page - 1]
        text_block_doc = await book_service.book_repository.get_text_block_by_id(
            text_block_id
        )

        if not text_block_doc:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Страница не найдена"},
            )

        text_block = {
            "_id": str(text_block_doc["_id"]),
            "original": text_block_doc.get("original", ""),
            "numberChapter": text_block_doc.get("numberChapter", 0),
            "summary": text_block_doc.get("summary"),
            "summaryTime": text_block_doc.get("summaryTime"),
            "questions": text_block_doc.get("questions", []),
            "rightAnswers": text_block_doc.get("rightAnswers", []),
        }

        return JSONResponse(status_code=200, content=text_block)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Ошибка при получении страницы книги: {str(e)}",
            },
        )
