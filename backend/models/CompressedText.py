from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId


class CompressedText(BaseModel):
    idCompressed: str = Field(default_factory=lambda: str(ObjectId()))
    bookId: str
    title: str
    originalText: str
    compressedText: str
    compressionDate: datetime
    compressionPercent: int

    def to_document(self) -> dict:
        """
        Преобразует объект CompressedText в документ для MongoDB.
        """
        return {
            "_id": ObjectId(self.idCompressed),
            "bookId": ObjectId(self.bookId),
            "title": self.title,
            "originalText": self.originalText,
            "compressedText": self.compressedText,
            "compressionDate": self.compressionDate,
            "compressionPercent": self.compressionPercent,
        }

    @classmethod
    def from_document(cls, document: dict):
        """
        Создает объект CompressedText из документа MongoDB.
        """
        return cls(
            idCompressed=str(document["_id"]),
            bookId=str(document["bookId"]),
            title=document["title"],
            originalText=document["originalText"],
            compressedText=document["compressedText"],
            compressionDate=document["compressionDate"],
            compressionPercent=document["compressionPercent"],
        )
