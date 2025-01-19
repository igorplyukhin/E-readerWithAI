from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from Utils.ReadSettings import get_setting
from pymongo.results import UpdateResult
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class BookRepository:
    def __init__(self):
        self.client = AsyncIOMotorClient(get_setting("DbConnectionString"))
        self.db = self.client[get_setting("DbName")]
        self.books_collection = self.db["books"]
        self.text_blocks_collection = self.db["text_blocks"]
        self.compressed_text_blocks_collection = self.db["compressed_text_blocks"] 
        self.users_collection = self.db["users"]

    async def insert_book(self, book_dict):
        result = await self.books_collection.insert_one(book_dict)
        return str(result.inserted_id)

    async def insert_text_blocks(self, text_block_documents):
        result = await self.text_blocks_collection.insert_many(text_block_documents)
        return [str(obj_id) for obj_id in result.inserted_ids]

    async def update_book_text_block_ids(self, book_id, text_block_ids):
        await self.books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": {"textBlockIds": text_block_ids}}
        )

    async def update_user_books(self, user_id, book_id):
        await self.users_collection.update_one(
            {"_id": user_id},
            {"$addToSet": {"bookIds": book_id}, "$inc": {"countBook": 1}}
        )

    async def get_book_by_id(self, book_id):
        object_id = ObjectId(book_id)
        return await self.books_collection.find_one({"_id": object_id})

    async def get_text_blocks_by_ids(self, text_block_ids):
        object_id_list = [ObjectId(tid) for tid in text_block_ids]
        return await self.text_blocks_collection.find({"_id": {"$in": object_id_list}}).to_list(length=None)

    async def get_text_block_by_id(self, text_block_id):
        object_id = ObjectId(text_block_id)
        return await self.text_blocks_collection.find_one({"_id": object_id})

    async def update_book_field(self, book_id: str, field_name: str, value) -> UpdateResult:
        try:
            result = await self.books_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {field_name: value}}
            )
            return result  # Возвращаем результат
        except Exception as e:
            logger.error(f"Ошибка при обновлении поля {field_name} книги с ID {book_id}: {e}")
            raise Exception(f"Ошибка при обновлении поля книги: {e}")
        
    async def update_book_progress_by_block(self, book_id: str, block_stop_book: int, total_pages: int) -> dict:
        try:
            logger.info(f"Запрос на обновление прогресса: book_id={book_id}, block_stop_book={block_stop_book}, total_pages={total_pages}")

            # Получаем книгу
            book = await self.get_book_by_id(book_id)
            if not book:
                raise Exception(f"Книга с ID {book_id} не найдена")

            # Проверяем корректность total_pages
            if total_pages <= 0:
                raise Exception("Некорректное количество страниц для расчёта прогресса")

            # Рассчитываем прогресс
            progress = int(((block_stop_book + 1) / total_pages) * 100)
            logger.info(f"Рассчитанный прогресс: {progress}% (block_stop_book={block_stop_book}, total_pages={total_pages})")

            # Обновляем `blockStopBook` и `progress`
            result = await self.books_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {"blockStopBook": block_stop_book, "progress": progress}}
            )
            if result.matched_count == 0:
                raise Exception(f"Не удалось обновить книгу с ID {book_id}")

            logger.info(f"Прогресс книги {book_id} успешно обновлён: blockStopBook={block_stop_book}, progress={progress}%")
            return {"blockStopBook": block_stop_book, "progress": progress}
        except Exception as e:
            logger.error(f"Ошибка при обновлении прогресса книги {book_id}: {e}")
            raise Exception(f"Ошибка при обновлении прогресса книги: {e}")


    async def save_compressed_blocks(self, book_id: str, compression_level: int, compressed_blocks: List[str]) -> List[str]:
        try:
            # Получаем документ книги
            book = await self.get_book_by_id(book_id)
            if not book:
                logger.error(f"Книга с ID {book_id} не найдена.")
                raise Exception("Книга не найдена")

            # Обновляем compressedText
            compressed_text = book.get("compressedText", {})
            compression_key = str(compression_level)

            # Проверяем существующие данные и добавляем/обновляем блоки
            compressed_text[compression_key] = compressed_blocks
            logger.info(f"Обновляем поле compressedText для книги {book_id}: {compressed_text}")

            # Сохраняем изменения
            update_result = await self.update_book_field(book_id, "compressedText", compressed_text)
            if not update_result:
                logger.error(f"Не удалось обновить поле compressedText для книги {book_id}.")
                raise Exception(f"Не удалось обновить поле compressedText для книги {book_id}.")

            logger.info(f"Сжатые блоки успешно сохранены для книги {book_id}, уровень сжатия: {compression_level}.")
            return compressed_blocks
        except Exception as e:
            logger.error(f"Ошибка при сохранении сжатых блоков для книги {book_id}: {e}")
            raise Exception(f"Ошибка при сохранении сжатых блоков: {e}")


    async def insert_compressed_block(self, book_id: str, compression_level: int, content: str) -> str:
        try:
            compressed_block = {
                "content": content,
                "compressionLevel": compression_level,
                "bookId": book_id
            }
            result = await self.compressed_text_blocks_collection.insert_one(compressed_block)
            logger.info(f"Сжатый блок успешно добавлен с ID {result.inserted_id} для книги {book_id}.")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Ошибка при вставке сжатого блока для книги {book_id}: {e}")
            raise Exception(f"Ошибка при вставке сжатого блока: {e}")
        
    async def get_compressed_blocks_by_ids(self, block_ids: List[str]) -> List[Dict]:
        object_ids = [ObjectId(block_id) for block_id in block_ids]
        blocks = await self.compressed_text_blocks_collection.find(
            {"_id": {"$in": object_ids}}
        ).to_list(length=len(block_ids))
        return blocks