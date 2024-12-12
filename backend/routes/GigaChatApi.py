from fastapi import FastAPI, File, Query, UploadFile, Form, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal, Optional
from utils.AppealToGigaChat import choice_action
from utils.compressed_text_service import CompressedTextService
from datetime import datetime
import json

app = FastAPI()
gigachat_router = APIRouter()
compressed_text_service = CompressedTextService()


class InputData(BaseModel):
    action: Literal["compress", "tests"]
    number: int


@gigachat_router.post(
    "/appendToGigachat/",
    summary="Загрузка файла и выбор операции",
    description="",
    tags=["Работа с GigaChat"],
)
async def upload_file(
    file: UploadFile = File(
        ..., media_type="application/pdf", description="Книга в формате PDF"
    ),
    action: Literal["compress", "tests"] = Query(
        "compress", description="Действие: сжать текст или сгенерировать тесты"
    ),
    percent_compress: Optional[int] = Query(50, description="На сколько % сжать текст"),
    custom_promt: Optional[str] = Query(
        None, description="Свой промт (необязательное)"
    ),
    temperature: Optional[float] = Query(
        None, description="Температура модели (необязательное)"
    ),
    top_p: Optional[float] = Query(
        None, description="Альтернатива температуре (необязательное)"
    ),
):
    # Проверка формата файла
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Проверка значений
    if action not in ["compress", "tests"]:
        return JSONResponse(status_code=400, content={"message": "Invalid action"})

    if not (10 <= percent_compress <= 90):
        return JSONResponse(
            status_code=400,
            content={"message": "Процент сжатия должен быть от 10 до 90 процентов!"},
        )

    if temperature is not None and not (0 <= temperature <= 2):
        return JSONResponse(
            status_code=400,
            content={"message": "Значение температуры должно быть от 0 до 2!"},
        )

    if top_p is not None and not (0 <= top_p <= 2):
        return JSONResponse(
            status_code=400,
            content={"message": "Значение top_p должно быть от 0 до 2!"},
        )

    # Получаем сжатый текст
    result = await choice_action(
        file, action, percent_compress, custom_promt, temperature, top_p
    )

    if action == "compress":
        try:
            # Сохраняем сжатый текст в базу данных
            compressed_id = await compressed_text_service.save_compressed_text(
                book_id=file.filename,  # Временно используем имя файла как ID книги
                title=file.filename,
                original_text="",  # Здесь нужно добавить получение оригинального текста
                compressed_text=result,
                compression_percent=percent_compress,
            )

            return {
                "compress_text": result,
                "compressed_id": compressed_id,
                "book_title": file.filename,
                "compression_date": datetime.now().strftime("%d/%m/%Y"),
                "compression_percent": percent_compress,
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error saving compressed text: {str(e)}"
            )

    elif action == "tests":
        return json.loads(result)


# Добавляем новые эндпоинты для работы со сжатым текстом
@gigachat_router.get(
    "/compressed/{compressed_id}",
    summary="Получение сжатого текста по ID",
    description="Возвращает сжатый текст по его идентификатору",
    tags=["Работа с GigaChat"],
)  # Тот же тег, что и у основного endpoint
async def get_compressed(compressed_id: str):
    compressed = await compressed_text_service.get_compressed_text(compressed_id)
    if not compressed:
        raise HTTPException(status_code=404, detail="Compressed text not found")
    return compressed


@gigachat_router.get(
    "/book/{book_id}/compressions",
    summary="Получение всех сжатых версий книги",
    description="Возвращает все сжатые версии текста для конкретной книги",
    tags=["Работа с GigaChat"],
)  # Тот же тег, что и у основного endpoint
async def get_book_compressions(book_id: str):
    compressions = await compressed_text_service.get_book_compressions(book_id)
    return compressions


app.include_router(gigachat_router)
