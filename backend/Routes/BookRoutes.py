import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Body
from fastapi.responses import JSONResponse
import aiofiles
from Services.BookService import BookService
from models.BookPageResponse import BookPageResponse
from models.CompressionUpdateRequest import CompressionUpdateRequest
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
    bookId: str = Query(..., description="ID книги")
):
    """
    Исправленный метод get_book_detail, который берёт сжатые блоки 
    из коллекции compressed_text_blocks через get_compressed_blocks_by_ids(...).
    """
    try:
        # Получение документа книги
        book_doc = await book_service.book_repository.get_book_by_id(bookId)
        if not book_doc:
            raise HTTPException(status_code=404, detail="Книга не найдена")

        # Получение идентификаторов текстовых блоков
        text_block_ids = book_doc.get("textBlockIds", [])
        
        # Извлекаем оригинальные (несжатые) текстовые блоки, если нужно
        original_text_blocks = []
        for block_id in text_block_ids:
            block_doc = await book_service.book_repository.get_text_block_by_id(block_id)
            if block_doc:
                original_text_blocks.append(block_doc.get("original", ""))

        # Обработка сжатых текстов
        compressed_text = book_doc.get("compressedText", {"25": [], "50": [], "75": []})

        # Для каждого уровня сжатия берём ID блоков из коллекции compressed_text_blocks
        for compression_key, block_ids in compressed_text.items():
            # Запрашиваем документы именно в compressed_text_blocks
            compressed_docs = await book_service.book_repository.get_compressed_blocks_by_ids(block_ids)
            # У каждого документа, скорее всего, поле "content" 
            # (в вашем примере: 'content': "...", 'compressionLevel': 25, 'bookId': ...)
            compressed_text[compression_key] = [
                doc.get("content", "") for doc in compressed_docs if doc
            ]

        # Формирование ответа
        response = {
            "title": book_doc.get("title", "Без названия"),
            "authors": book_doc.get("author", "Неизвестен"),
            "annotation": book_doc.get("annotation", ""),
            "progress": book_doc.get("progress", 0),
            "totalPages": len(text_block_ids),
            "textBlocks": original_text_blocks,
            "compressedText": compressed_text,  # уже подставлены правильные content
            "status": book_doc.get("status", "reading"),
            "compressionLevel": book_doc.get("compressionLevel", 0)
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
    
@book_router.put("/api/book/updateCompressionLevel", summary="Обновить уровень сжатия книги")
async def update_compression_level(
    bookId: str = Query(..., description="ID книги"),
    request: CompressionUpdateRequest = Body(...)
):
    try:
        logging.info(f"Received request to update compression level for bookId={bookId}, compressionLevel={request.compressionLevel}")
        
        # Проверяем границы значений
        if not (0 <= request.compressionLevel <= 75):
            raise HTTPException(status_code=400, detail="Уровень сжатия должен быть от 0 до 75")
        
        # Обновляем уровень сжатия через репозиторий
        result = await book_service.book_repository.update_book_field(bookId, "compressionLevel", request.compressionLevel)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Книга не найдена или не удалось обновить")


        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Книга не найдена или не удалось обновить")

        return JSONResponse(content={"status": "success", "message": "Уровень сжатия успешно обновлен"})
    except Exception as e:
        logging.error(f"Error updating compression level for bookId={bookId}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления уровня сжатия: {str(e)}")




