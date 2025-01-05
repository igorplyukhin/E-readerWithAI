from typing import List, Literal, Optional
from fastapi import FastAPI, Query, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import json
from Services.GigaChatServices import choice_action
from Repositories.BookRepository import BookRepository  # Репозиторий для работы с книгами
import logging

app = FastAPI()
gigachat_router = APIRouter()
logger = logging.getLogger(__name__)

# Инициализация репозиториев
book_repository = BookRepository()

@gigachat_router.post("/api/gigachat/compress-book", summary="Сжатие текста книги", description="Сжимает текст книги на указанный уровень", tags=["Работа с GigaChat"])
async def compress_book(
    book_id: str,
    compression_level: int = Query(..., description="Уровень сжатия (25, 50, 75)"),
):
    try:
        # Проверка корректности уровня сжатия
        if compression_level not in [25, 50, 75]:
            logger.error(f"Неверный уровень сжатия: {compression_level}.")
            raise HTTPException(status_code=400, detail="Уровень сжатия должен быть одним из [25, 50, 75].")

        # Извлечение книги из базы данных
        book = await book_repository.get_book_by_id(book_id)
        if not book:
            logger.error(f"Книга с ID {book_id} не найдена.")
            raise HTTPException(status_code=404, detail="Книга с указанным ID не найдена.")

        # Проверка наличия текстовых блоков
        if "textBlockIds" not in book or not book["textBlockIds"]:
            logger.error(f"Книга с ID {book_id} не содержит текстовых блоков.")
            raise HTTPException(status_code=400, detail="У книги отсутствуют текстовые блоки.")

        # Проверка наличия уже сжатых блоков
        compressed_texts = book.get("compressedText", {})
        compression_key = str(compression_level)

        if compression_key in compressed_texts and compressed_texts[compression_key]:
            # Если сжатие уже выполнено, возвращаем сохранённые данные
            logger.info(f"Сжатие на уровне {compression_level}% уже выполнено для книги {book_id}.")
            compressed_block_ids = compressed_texts[compression_key]
            compressed_blocks = await book_repository.get_compressed_blocks_by_ids(compressed_block_ids)

            if not compressed_blocks:
                logger.error(f"Сжатые блоки для книги {book_id} на уровне {compression_level}% не найдены.")
                raise HTTPException(status_code=404, detail="Сжатые блоки не найдены.")

            # Возвращаем массив страниц
            return {
                "book_id": book_id,
                "compression_level": compression_level,
                "pages": [block["content"] for block in compressed_blocks],  # Массив страниц
            }

        # Извлечение текстовых блоков
        text_blocks = await book_repository.get_text_blocks_by_ids(book["textBlockIds"])
        if not text_blocks:
            logger.error(f"Текстовые блоки для книги с ID {book_id} не найдены.")
            raise HTTPException(status_code=404, detail="Текстовые блоки не найдены.")

        # Выполнение сжатия
        compressed_blocks = await choice_action(
            text_blocks=text_blocks,
            action="compress",
            percent_compress=compression_level,
            prompt=None,
            temperature=None,
            top_p=None,
            book=book,
            book_id=book_id,
        )

        if not compressed_blocks:
            logger.error(f"Не удалось сжать текст для книги с ID {book_id}.")
            raise HTTPException(status_code=500, detail="Ошибка при сжатии текста.")

        # Сохранение сжатых блоков
        compressed_block_ids = await book_repository.save_compressed_blocks(book_id, compression_level, compressed_blocks)
        if not compressed_block_ids:
            logger.error(f"Не удалось сохранить сжатые блоки для книги {book_id}.")
            raise HTTPException(status_code=500, detail="Не удалось сохранить сжатые блоки.")

        # Обновление книги
        book["compressedText"] = book.get("compressedText", {})
        book["compressedText"][compression_key] = compressed_block_ids

        update_result = await book_repository.update_book_field(book_id, "compressedText", book["compressedText"])
        if not update_result:
            logger.error(f"Ошибка при обновлении compressedText для книги {book_id}.")
            raise HTTPException(status_code=500, detail="Ошибка при обновлении данных книги.")

        logger.info(f"Сжатие текста на уровне {compression_level}% завершено для книги {book_id}.")

        # Возвращаем массив страниц
        return {
            "book_id": book_id,
            "compression_level": compression_level,
            "pages": compressed_blocks,  # Массив страниц
        }

    except HTTPException as http_exc:
        logger.error(f"HTTP ошибка при обработке книги {book_id}: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Неизвестная ошибка при сжатии книги {book_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки книги: {str(e)}")


@gigachat_router.post("/api/gigachat/simple-chat", summary="Обычный диалог", description="",
                      tags=["Работа с GigaChat"])
async def simple_chat(
    message: str = Query(..., description="Сообщение GigaChat-у"),
    custom_promt: Optional[str] = Query(None, description="Свой промт (необязательное)"),
    temperature: Optional[float] = Query(None, description="Температура модели (необязательное)"),
    top_p: Optional[float] = Query(None, description="Альтернатива температуре (необязательное, https://developers.sber.ru/docs/ru/gigachat/api/reference-grpc)")
) -> JSONResponse:

    if not message.strip():
        raise HTTPException(status_code=400, detail="Введите сообщение!")
    
    if temperature is not None and not (0 <= temperature <= 2):
        raise HTTPException(status_code=400, detail="Значение температуры должно быть от 0 до 2!")
        
    if top_p is not None and not (0 <= top_p <= 2):
        raise HTTPException(status_code=400, detail="Значение top_p должно быть от 0 до 2!")
    
    result = await choice_action(None, "dialog", None, custom_promt, temperature, top_p, message)
    return {"answer": result}
