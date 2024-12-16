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
