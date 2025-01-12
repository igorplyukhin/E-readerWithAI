import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Body
from fastapi.responses import JSONResponse
import aiofiles
from Services.BookService import BookService
from models.CompressionUpdateRequest import CompressionUpdateRequest
import logging

book_router = APIRouter()
book_service = BookService()

logger = logging.getLogger(__name__)


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
    
@book_router.patch("/api/book/updateProgress", summary="Обновить прогресс чтения книги", tags=["Загрузка и работа с файлами"])
async def update_book_progress(
    bookId: str = Query(..., description="ID книги"),
    blockStopBook: int = Query(..., description="Номер текущего прочитанного блока"),
    totalPages: int = Query(..., description="Общее количество страниц текущего текста")
):
    try:
        logger.info(f"Запрос на обновление прогресса: bookId={bookId}, blockStopBook={blockStopBook}, totalPages={totalPages}")

        # Обновляем прогресс через репозиторий
        update_result = await book_service.book_repository.update_book_progress_by_block(bookId, blockStopBook, totalPages)
        if not update_result:
            raise HTTPException(status_code=404, detail="Книга не найдена")

        logger.info(f"Прогресс книги {bookId} успешно обновлён")
        return JSONResponse(
            status_code=200,
            content={"blockStopBook": blockStopBook, "progress": update_result["progress"]},
        )

    except HTTPException as http_exc:
        logger.warning(f"HTTP ошибка: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Ошибка при обновлении прогресса книги: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления прогресса: {str(e)}")

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
            "annotation": book_doc.get("annotation", None),
            "progress": book_doc.get("progress", 0),
            "totalPages": len(text_block_ids),
            "textBlocks": original_text_blocks,
            "blockStopBook": book_doc.get("blockStopBook", 0),  
            "chapterStopBook": book_doc.get("chapterStopBook", 0), 
            "status": book_doc.get("status", "reading"),
            "compressionLevel": book_doc.get("compressionLevel", 0),
            "compressedText": compressed_text
        }

        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения книги: {str(e)}")

@book_router.put("/api/book/updateCompressionLevel", summary="Обновить уровень сжатия книги", description="",
                 tags=["Загрузка и работа с файлами"])
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




