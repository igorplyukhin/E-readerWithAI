import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import aiofiles
from Services.BookService import BookService
from models.BookPageResponse import BookPageResponse
import logging

book_router = APIRouter()
book_service = BookService()


@book_router.post("/api/book/upload", summary="Загрузить новую книгу", description="",
                  tags=["Загрузка и работа с файлами"])
async def upload_book(
    user_id: str = Query(..., description="ID пользователя"),
    file: UploadFile = File(..., description="Книга в формате PDF или FB2")
):
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = os.path.join(upload_dir, file.filename or "default.fb2")
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {str(e)}")
    
    try:
        book_dict = await book_service.process_uploaded_book(file_path, file.filename, user_id)
        return JSONResponse(content={
            "status": "success",
            "message": "Книга успешно загружена и обработана",
            "book": book_dict
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки книги: {str(e)}")


@book_router.get("/api/book/detail", summary="Получить детали книги", description="",
                 tags=["Загрузка и работа с файлами"])
async def get_book_detail(
    bookId: str = Query(..., description="ID книги")  # Исправлено с id на bookId
):
    try:
        # Получение документа книги
        book_doc = await book_service.book_repository.get_book_by_id(bookId)
        if not book_doc:
            raise HTTPException(status_code=404, detail="Книга не найдена")

        # Получение идентификаторов текстовых блоков
        text_block_ids = book_doc.get("textBlockIds", [])
        
        # Извлечение текстовых блоков
        text_blocks = [
            await book_service.book_repository.get_text_block_by_id(block_id)
            for block_id in text_block_ids
        ]
        text_blocks = [block.get("original", "") for block in text_blocks if block]

        # Формирование ответа
        response = {
            "title": book_doc.get("title", "Без названия"),
            "authors": book_doc.get("author", "Неизвестен"),
            "annotation": book_doc.get("annotation", ""),
            "progress": book_doc.get("progress", 0),
            "totalPages": len(text_block_ids),
            "textBlocks": text_blocks,
            "status": book_doc.get("status", "reading")
        }

        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения книги: {str(e)}")


@book_router.get("/api/book/page", summary="Получить страницу книги", description="",
                 tags=["Загрузка и работа с файлами"])
async def get_book_page(
    bookId: str = Query(..., description="ID книги"),
    page: int = Query(1, description="Номер страницы (начиная с 1)")
):
    logging.info(f"Получен запрос: bookId={bookId}, page={page}")

    if page < 1:
        logging.error("Номер страницы меньше 1")
        raise HTTPException(status_code=400, detail="Номер страницы должен быть больше или равен 1")

    try:
        # Получаем данные книги по ID
        book_doc = await book_service.book_repository.get_book_by_id(bookId)
        if not book_doc:
            logging.error(f"Книга с ID {bookId} не найдена")
            raise HTTPException(status_code=404, detail="Книга не найдена")

        # Проверяем наличие текстовых блоков
        text_block_ids = book_doc.get("textBlockIds", [])
        logging.info(f"Количество текстовых блоков: {len(text_block_ids)}")
        if page > len(text_block_ids):
            logging.error(f"Запрошенная страница {page} превышает количество страниц {len(text_block_ids)}")
            raise HTTPException(status_code=404, detail="Страница не найдена")

        # Получаем текстовый блок по ID
        text_block_id = text_block_ids[page - 1]
        text_block_doc = await book_service.book_repository.get_text_block_by_id(text_block_id)
        if not text_block_doc:
            logging.error(f"Текстовый блок с ID {text_block_id} не найден")
            raise HTTPException(status_code=404, detail="Текстовый блок не найден")

        # Формируем ответ
        response = BookPageResponse(
            pageNumber=page,
            totalPages=len(text_block_ids),
            content=text_block_doc.get("original", "")
        )
        logging.info(f"Успешно возвращена страница {page} для книги {bookId}")
        return response

    except Exception as e:
        logging.exception(f"Ошибка получения страницы книги {bookId}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения страницы книги: {str(e)}")

