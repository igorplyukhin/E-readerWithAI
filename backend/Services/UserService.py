from fastapi import HTTPException
from models.UserBooksResponse import UserBooksResponse
from models.User import User
from models.Book import Book
from Repositories.UserRepository import UserRepository

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    async def get_user(self, login: str):
        user_doc = await self.user_repository.find_user_by_login(login)
        if user_doc is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user = User(
            idUser=user_doc["_id"],
            password=user_doc.get("password", ""),
            bookIds=user_doc.get("bookIds", []),
            countBook=user_doc.get("countBook", 0)
        )

        books = []
        if user.bookIds:
            book_docs = await self.user_repository.get_books_by_user(user.bookIds)
            for doc in book_docs:
                book = Book(
                    idBook=str(doc["_id"]),
                    title=doc.get("title", ""),
                    author=doc.get("author", ""),
                    description=doc.get("description", ""),
                    annotation=doc.get("annotation"),
                    status=doc.get("status", "reading"),
                    mode=doc.get("mode", "default"),
                    nameFile=doc.get("nameFile", ""),
                    filePath=doc.get("filePath", ""),
                    blockStopBook=doc.get("blockStopBook", 0),
                    chapterStopBook=doc.get("chapterStopBook", 0),
                    textBlockIds=[str(tid) for tid in doc.get("textBlockIds", [])],
                    progress=doc.get("progress", 0),
                    compressionLevel=doc.get("compressionLevel", 0)  
                )
                books.append(book)

        return UserBooksResponse(count_book=len(books), books=books)

    async def register_user(self, login: str, password: str):
        existing_user = await self.user_repository.find_user_by_login(login)
        if existing_user:
            raise HTTPException(status_code=409, detail="Пользователь с таким логином уже существует")

        new_user = {"_id": login, "password": password}
        await self.user_repository.insert_user(new_user)

    async def login_user(self, login: str, password: str):
        user_doc = await self.user_repository.find_user_by_login(login)
        if user_doc and user_doc.get("password") == password:
            response = {"status": "success", "message": "Аутентификация успешна", "userId": login}
            return response
        
        raise HTTPException(status_code=401, detail="Неверный пароль или пользователь не найден")

    async def update_user_password(self, login: str, new_password: str, old_password: str):
        user_doc = await self.user_repository.find_user_by_login(login)
        if user_doc and user_doc.get("password") == old_password:
            result = await self.user_repository.update_user_password(login, new_password)
            if result.modified_count > 0:
                return {"message": "Пароль успешно обновлен"}
            else:
                raise HTTPException(status_code=500, detail="Не удалось обновить пароль")
        else:
            raise HTTPException(status_code=401, detail="Старый пароль неверен или пользователь не найден")

    async def delete_user(self, login: str, password: str):
        user_doc = await self.user_repository.find_user_by_login(login)
        if user_doc and user_doc.get("password") == password:
            result = await self.user_repository.delete_user(login)
            if result.deleted_count > 0:
                return {"message": "Пользователь успешно удален"}
            else:
                raise HTTPException(status_code=500, detail="Не удалось удалить пользователя")
        else:
            raise HTTPException(status_code=401, detail="Неверный пароль или пользователь не найден")
