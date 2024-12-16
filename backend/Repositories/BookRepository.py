from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi import HTTPException
from models.Book import Book
from models.TextBlock import TextBlock
from Utils.ReadSettings import get_setting

class BookRepository:
    def __init__(self):
        self.client = AsyncIOMotorClient(get_setting("DbConnectionString"))
        self.db = self.client[get_setting("DbName")]
        self.books_collection = self.db["books"]
        self.text_blocks_collection = self.db["text_blocks"]
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
