from fastapi import FastAPI

<<<<<<< HEAD
from routes.BookRoutes import book_router
from routes.UserRoutes import user_router
from routes.GigaChatRoutes import gigachat_router
from routes.CompressedBook import compressed_book_router
=======
from Routes.BookRoutes import book_router
from Routes.UserRoutes import user_router
from Routes.GigaChatRoutes import gigachat_router
from Routes.CompressedBook import compressed_book_router
>>>>>>> origin/backend_python

app = FastAPI()

app.include_router(book_router)
app.include_router(user_router)
app.include_router(gigachat_router)
app.include_router(compressed_book_router)
<<<<<<< HEAD


from fastapi import FastAPI
from utils.ReadSettings import get_setting

app = FastAPI()
=======
>>>>>>> origin/backend_python
