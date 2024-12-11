from typing import List
from pydantic import BaseModel, Field

class User(BaseModel):
    idUser: str
    password: str = ""
    bookIds: List[str] = Field(default_factory=list)
    countBook: int = 0
