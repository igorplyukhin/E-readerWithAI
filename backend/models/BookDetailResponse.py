from typing import List, Optional
from pydantic import BaseModel, Field

class BookDetailResponse(BaseModel):
    title: str = Field(..., description="Название книги")  # Добавляем поле для названия книги
    authors: str = Field(..., description="Авторы книги")  # Добавляем поле для авторов
    annotation: Optional[str] = Field(None, description="Аннотация книги")  # Поле может быть опциональным
    progress: int = Field(..., description="Прогресс чтения книги в процентах")  # Прогресс в процентах
    totalPages: int = Field(..., description="Общее количество страниц в книге")
    textBlocks: List[str] = Field(..., description="Список идентификаторов текстовых блоков")
    status: str = Field(..., description="Статус книги (чтение, завершено и т.д.)")  # Статус чтения книги
