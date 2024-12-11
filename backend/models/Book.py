from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class Book(BaseModel):
    idBook: str = Field(default_factory=lambda: str(ObjectId()))
    title: str
    author: str
    description: str
    annotation: Optional[str] = None
    status: str = "reading"
    mode: str = "default"
    nameFile: str
    filePath: str
    blockStopBook: int = 0
    chapterStopBook: int = 0
    textBlockIds: List[str] = Field(default_factory=list)

    def to_document(self) -> dict:
        """
        Преобразует объект Book в документ (dict), который можно вставлять в MongoDB.
        """
        return {
            "_id": ObjectId(self.idBook),
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "annotation": self.annotation,
            "status": self.status,
            "mode": self.mode,
            "nameFile": self.nameFile,
            "filePath": self.filePath,
            "blockStopBook": self.blockStopBook,
            "chapterStopBook": self.chapterStopBook,
            "textBlockIds": [ObjectId(tid) for tid in self.textBlockIds]
        }
