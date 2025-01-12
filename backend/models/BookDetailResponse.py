from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class BookDetailResponse(BaseModel):
    title: str = Field(..., description="Название книги")  # Название книги
    authors: str = Field(..., description="Авторы книги")  # Авторы книги
    annotation: Optional[str] = Field(None, description="Аннотация книги")  # Аннотация может быть опциональной
    progress: int = Field(..., ge=0, le=100, description="Прогресс чтения книги в процентах")  # Прогресс в процентах
    totalPages: int = Field(..., ge=1, description="Общее количество страниц в книге")  # Минимум 1 страница
    textBlocks: List[str] = Field(..., description="Список идентификаторов текстовых блоков")
    blockStopBook: int = Field(default=0, description="Номер последнего прочитанного блока")
    chapterStopBook: int = Field(default=0, description="Номер последней прочитанной главы")
    status: str = Field(..., description="Статус книги (например, чтение, завершено и т.д.)")
    compressionLevel: int = Field(default=0, ge=0, le=75, description="Уровень сжатия текста книги")
    compressedText: Dict[str, List[str]] = Field(
        default_factory=lambda: {"25": [], "50": [], "75": []},
        description="Сжатые тексты по уровням сжатия (25, 50, 75)"
    )