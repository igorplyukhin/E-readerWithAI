from typing import Optional
from pydantic import BaseModel

class BookText(BaseModel):
    title: str
    authors: str
    content: str
    annotation: Optional[str] = None
