from dataclasses import dataclass
from typing import Optional

@dataclass
class BookResponse:
    status: str
    message: str
    book: Optional['Book'] = None