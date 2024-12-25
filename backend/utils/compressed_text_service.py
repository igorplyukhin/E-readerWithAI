from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompressedTextService:
    def __init__(self):
        self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.client["book_compressor"]
        self.collection = self.db["compressed_texts"]

    def split_text_into_blocks(self, text: str, block_size: int = 1000) -> list:
        """
        Разделяет текст на блоки по 1000 символов
        """
        return [text[i : i + block_size] for i in range(0, len(text), block_size)]

    async def save_compressed_text(
        self,
        book_id: str,
        title: str,
        original_text: str,
        compressed_text: str,
        compression_percent: int,
    ) -> str:
        try:
            # Разделяем сжатый текст на блоки
            text_blocks = self.split_text_into_blocks(compressed_text)

            doc_id = ObjectId()
            document = {
                "_id": doc_id,
                "bookId": book_id,
                "title": title,
                "originalText": original_text,
                "compressedText": compressed_text,
                "textBlocks": text_blocks,  # Массив блоков текста
                "totalBlocks": len(text_blocks),  # Общее количество блоков
                "compressionDate": datetime.now(),
                "compressionPercent": compression_percent,
            }

            await self.collection.insert_one(document)
            logger.info(f"Документ сохранен в MongoDB с ID: {doc_id}")
            return str(doc_id)

        except Exception as e:
            logger.error(f"Ошибка при сохранении в MongoDB: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error saving compressed text: {str(e)}"
            )

    async def get_compressed_text(self, compressed_id: str):
        try:
            obj_id = ObjectId(compressed_id)
            result = await self.collection.find_one({"_id": obj_id})
            if result:
                result["_id"] = str(result["_id"])
                return result
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении сжатого текста: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error retrieving compressed text: {str(e)}"
            )

    async def check_connection(self):
        try:
            await self.db.command("ping")
            logger.info("Успешное подключение к MongoDB")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к MongoDB: {str(e)}")
            return False
