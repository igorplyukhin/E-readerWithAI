from typing import List
from pydantic import BaseModel
from models.Book import Book 

class UserBooksResponse(BaseModel):
    count_book: int
    books: List[Book]
