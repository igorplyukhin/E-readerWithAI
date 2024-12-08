from fastapi import FastAPI

from routes.BookRoutes import book_router
from routes.TextRoutes import text_router
from routes.Test import test_router
from routes.UserRoutes import user_router
from routes.GigaChatApi import gigachat_router

app = FastAPI()

app.include_router(test_router)
app.include_router(book_router)
app.include_router(text_router)
app.include_router(user_router)
app.include_router(gigachat_router)

