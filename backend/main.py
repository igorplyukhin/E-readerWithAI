from fastapi import FastAPI

from Routes.BookRoutes import book_router
from Routes.UserRoutes import user_router
from Routes.GigaChatRoutes import gigachat_router
from Routes.CompressedBook import compressed_book_router

app = FastAPI()

app.include_router(book_router)
app.include_router(user_router)
app.include_router(gigachat_router)
app.include_router(compressed_book_router)

# Добавляем подключение к MongoDB
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Получаем URL из переменных окружения
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://test:test@mongodb:27017/test?authSource=admin")

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    app.mongodb = app.mongodb_client.test

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
