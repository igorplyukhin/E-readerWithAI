from typing import List
from pydantic import BaseModel

class BookDetailResponse(BaseModel):
    annotation: str
    totalPages: int
    textBlocks: List[str]