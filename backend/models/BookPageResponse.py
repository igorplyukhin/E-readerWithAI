from pydantic import BaseModel

class BookPageResponse(BaseModel):
    pageNumber: int
    totalPages: int
    content: str
