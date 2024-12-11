from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from models.UserBooksResponse import UserBooksResponse
from models.User import User
from models.Book import Book

user_router = APIRouter()

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["database"]
users_collection = db["users"]
books_collection = db["books"]

@user_router.post("/get_user")
async def get_user(login: str = Form(...)):
    if not login:
        raise HTTPException(status_code=400, detail="Логин не предоставлен")

    user_doc = await users_collection.find_one({"_id": login})
    if user_doc is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user = User(
        idUser=user_doc["_id"],
        password=user_doc.get("password", ""),
        bookIds=user_doc.get("bookIds", []),
        countBook=user_doc.get("countBook", 0)
    )

    if user.bookIds:
        object_id_list = [ObjectId(bid) for bid in user.bookIds]
        book_docs = await books_collection.find({"_id": {"$in": object_id_list}}).to_list(length=None)

        books = []
        for doc in book_docs:
            book = Book(
                idBook=str(doc["_id"]),
                title=doc.get("title", "Без названия"),
                author=doc.get("author", "Неизвестно"),
                description=doc.get("description", ""),
                annotation=doc.get("annotation"),
                status=doc.get("status", "reading"),
                mode=doc.get("mode", "default"),
                nameFile=doc.get("nameFile", ""),
                filePath=doc.get("filePath", ""),
                blockStopBook=doc.get("blockStopBook", 0),
                chapterStopBook=doc.get("chapterStopBook", 0),
                textBlockIds=doc.get("textBlockIds", [])
            )
            books.append(book)

        response = UserBooksResponse(
            count_book=len(books),
            books=books
        )
        return JSONResponse(status_code=200, content=response.model_dump())
    else:
        return JSONResponse(status_code=200, content=UserBooksResponse(count_book=0, books=[]).model_dump())

@user_router.post("/register")
async def register(login: str = Form(...), password: str = Form(...)):
    if not login or not password:
        raise HTTPException(status_code=400, detail="Логин или пароль не предоставлены")

    existing_user = await users_collection.find_one({"_id": login})

    if existing_user:
        raise HTTPException(status_code=409, detail="Пользователь с таким логином уже существует")

    new_user = {"_id": login, "password": password}
    await users_collection.insert_one(new_user)

    return JSONResponse(content={"status": "success", "message": "Пользователь успешно зарегистрирован", "userId": login})

@user_router.post("/login")
async def login(login: str = Form(...), password: str = Form(...)):
    if not login or not password:
        raise HTTPException(status_code=400, detail="Логин или пароль не предоставлены")

    user_doc = await users_collection.find_one({"_id": login})

    if user_doc and user_doc.get("password") == password:
        return JSONResponse(content={"status": "success", "message": "Аутентификация успешна", "userId": login})
    else:
        raise HTTPException(status_code=401, detail="Неверный пароль или пользователь не найден")

# Изменение пароля пользователя / После реализации на фронте убрать этот комментарий 
@user_router.post("/update_user")
async def update_user(login: str = Form(...), new_password: str = Form(...), old_password: str = Form(...)):
    if not login or not new_password or not old_password:
        raise HTTPException(status_code=400, detail="Не предоставлены необходимые параметры")

    user_doc = await users_collection.find_one({"_id": login})

    if user_doc and user_doc.get("password") == old_password:
        result = await users_collection.update_one(
            {"_id": login},
            {"$set": {"password": new_password}}
        )
        if result.modified_count > 0:
            return JSONResponse(content={"message": "Пароль успешно обновлен"})
        else:
            raise HTTPException(status_code=500, detail="Не удалось обновить пароль")
    else:
        raise HTTPException(status_code=401, detail="Старый пароль неверен или пользователь не найден")

# Удаления аккаунта пользователя / После реализации на фронте убрать этот комментарий 
@user_router.post("/delete_user")
async def delete_user(login: str = Form(...), password: str = Form(...)):
    if not login or not password:
        raise HTTPException(status_code=400, detail="Логин или пароль не предоставлен")

    user_doc = await users_collection.find_one({"_id": login})

    if user_doc and user_doc.get("password") == password:
        result = await users_collection.delete_one({"_id": login})
        if result.deleted_count > 0:
            return JSONResponse(content={"message": "Пользователь успешно удален"})
        else:
            raise HTTPException(status_code=500, detail="Не удалось удалить пользователя")
    else:
        raise HTTPException(status_code=401, detail="Неверный пароль или пользователь не найден")