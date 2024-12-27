from typing import Optional
from pydantic import BaseModel, Field
from models.Book import Book  

class BookResponse(BaseModel):
    status: str = Field(..., description="Статус ответа (e.g., 'success' или 'error')")
    message: str = Field(..., description="Сообщение об ошибке или успехе")
    book: Optional[Book] = Field(None, description="Детали книги, если запрос успешен")
