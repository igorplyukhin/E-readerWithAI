from typing import List, Optional
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class Book(BaseModel):
    idBook: str = Field(default_factory=lambda: str(ObjectId()))
    title: str
    author: str
    description: str
    annotation: Optional[str] = None
    status: str = Field(default="reading", description="Статус книги (e.g., 'reading', 'completed')")
    mode: str = Field(default="default", description="Режим книги")
    nameFile: str
    filePath: str
    blockStopBook: int = Field(default=0, description="Номер последнего прочитанного блока")
    chapterStopBook: int = Field(default=0, description="Номер последней прочитанной главы")
    textBlockIds: List[str] = Field(default_factory=list, description="Список идентификаторов текстовых блоков")
    progress: int = Field(default=0, ge=0, le=100, description="Прогресс чтения книги в процентах")
    compressionLevel: int = Field(default=0, ge=0, le=75, description="Уровень сжатия текста книги")  

    @validator("status")
    def validate_status(cls, value):
        allowed_statuses = ["reading", "completed", "paused"]
        if value not in allowed_statuses:
            raise ValueError(f"Недопустимый статус: {value}. Доступные статусы: {allowed_statuses}")
        return value

    @validator("mode")
    def validate_mode(cls, value):
        allowed_modes = ["default", "advanced"]
        if value not in allowed_modes:
            raise ValueError(f"Недопустимый режим: {value}. Доступные режимы: {allowed_modes}")
        return value

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
            "textBlockIds": [ObjectId(tid) for tid in self.textBlockIds],
            "progress": self.progress,
            "compressionLevel": self.compressionLevel,  # Добавлено новое поле
        }

    @classmethod
    def from_document(cls, doc: dict) -> "Book":
        """
        Преобразует документ MongoDB в объект Book.
        """
        return cls(
            idBook=str(doc["_id"]),
            title=doc.get("title", ""),
            author=doc.get("author", ""),
            description=doc.get("description", ""),
            annotation=doc.get("annotation"),
            status=doc.get("status", "reading"),
            mode=doc.get("mode", "default"),
            nameFile=doc.get("nameFile", ""),
            filePath=doc.get("filePath", ""),
            blockStopBook=doc.get("blockStopBook", 0),
            chapterStopBook=doc.get("chapterStopBook", 0),
            textBlockIds=[str(tid) for tid in doc.get("textBlockIds", [])],
            progress=doc.get("progress", 0),
            compressionLevel=doc.get("compressionLevel", 50),  # Добавлено новое поле
        )
