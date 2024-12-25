from typing import Optional
from pydantic import BaseModel
from models.Book import Book  

class BookResponse(BaseModel):
    status: str
    message: str
    book: Optional[Book] = None
