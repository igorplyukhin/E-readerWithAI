from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from Services.GigaChatServices import choice_action
from Repositories.CompressedBookRepository import CompressBookRepository


compressed_book_router = APIRouter()
compressed_text_service = CompressBookRepository()


class InputData(BaseModel):
    action: Literal["compress", "tests"]
    number: int


@compressed_book_router.get(
    "/api/compressed/{compressed_id}",
    summary="Получение сжатого текста по ID",
    description="Возвращает сжатый текст по его идентификатору",
    tags=["Сжатый текст"],
)  # Тот же тег, что и у основного endpoint
async def get_compressed(compressed_id: str):
    compressed = await compressed_text_service.get_compressed_text(compressed_id)
    if not compressed:
        raise HTTPException(status_code=404, detail="Compressed text not found")
    return compressed


@compressed_book_router.get(
    "/api/book/{book_id}/compressions",
    summary="Получение всех сжатых версий книги",
    description="Возвращает все сжатые версии текста для конкретной книги",
    tags=["Сжатый текст"],
)  # Тот же тег, что и у основного endpoint
async def get_book_compressions(book_id: str):
    compressions = await compressed_text_service.get_book_compressions(book_id)
    return compressions
