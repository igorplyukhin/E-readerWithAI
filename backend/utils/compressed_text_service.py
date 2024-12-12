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

    async def save_compressed_text(
        self,
        book_id: str,
        title: str,
        original_text: str,
        compressed_text: str,
        compression_percent: int,
    ) -> str:
        try:
            # Создаем новый ObjectId для документа
            doc_id = ObjectId()

            document = {
                "_id": doc_id,
                "bookId": book_id,  # Здесь оставляем строку, так как это временный идентификатор
                "title": title,
                "originalText": original_text,
                "compressedText": compressed_text,
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
            # Преобразуем строку в ObjectId
            obj_id = ObjectId(compressed_id)
            result = await self.collection.find_one({"_id": obj_id})
            if result:
                # Преобразуем ObjectId в строку для JSON-сериализации
                result["_id"] = str(result["_id"])
                return result
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении сжатого текста: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error retrieving compressed text: {str(e)}"
            )

    async def get_book_compressions(self, book_id: str):
        try:
            cursor = self.collection.find({"bookId": book_id})
            compressions = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                compressions.append(doc)
            return compressions
        except Exception as e:
            logger.error(f"Ошибка при получении сжатых текстов книги: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error retrieving book compressions: {str(e)}"
            )

    async def check_connection(self):
        try:
            await self.db.command("ping")
            logger.info("Успешное подключение к MongoDB")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к MongoDB: {str(e)}")
            return False
