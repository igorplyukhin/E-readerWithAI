from dataclasses import dataclass
from typing import List

@dataclass
class UserBooksResponse:
    count_book: int
    books: List['Book'] 