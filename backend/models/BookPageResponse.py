from dataclasses import dataclass

@dataclass
class BookPageResponse:
    pageNumber: int
    totalPages: int
    content: str