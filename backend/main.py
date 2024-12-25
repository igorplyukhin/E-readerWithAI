from fastapi import FastAPI

from routes.BookRoutes import book_router
from routes.UserRoutes import user_router
from routes.GigaChatRoutes import gigachat_router
from routes.CompressedBook import compressed_book_router

app = FastAPI()

app.include_router(book_router)
app.include_router(user_router)
app.include_router(gigachat_router)
app.include_router(compressed_book_router)


from fastapi import FastAPI
from utils.ReadSettings import get_setting

app = FastAPI()
