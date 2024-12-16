from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from models.User import User
from models.Book import Book
from Utils.ReadSettings import get_setting

class UserRepository:
    def __init__(self):
        client = AsyncIOMotorClient(get_setting("DbConnectionString"))
        db = client[get_setting("DbName")]
        self.users_collection = db["users"]
        self.books_collection = db["books"]

    async def find_user_by_login(self, login: str):
        return await self.users_collection.find_one({"_id": login})

    async def insert_user(self, user_data: dict):
        await self.users_collection.insert_one(user_data)

    async def update_user_password(self, login: str, new_password: str):
        return await self.users_collection.update_one(
            {"_id": login},
            {"$set": {"password": new_password}}
        )

    async def delete_user(self, login: str):
        return await self.users_collection.delete_one({"_id": login})

    async def get_books_by_user(self, book_ids: list):
        object_id_list = [ObjectId(bid) for bid in book_ids]
        return await self.books_collection.find({"_id": {"$in": object_id_list}}).to_list(length=None)
