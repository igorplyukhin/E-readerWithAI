from fastapi import FastAPI, File, Query, UploadFile, Form, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal, Optional
from Services.GigaChatServices import choice_action
import json
from datetime import datetime

from Repositories.CompressedBookRepository import CompressBookRepository
<<<<<<< HEAD
from Repositories.BookRepository import BookRepository
from Services.GigaChatServices import get_author_info

book_repo = BookRepository()
=======

>>>>>>> origin/backend_python
app = FastAPI()
gigachat_router = APIRouter()
compressed_text_service = CompressBookRepository()

<<<<<<< HEAD

@gigachat_router.post(
    "/api/gigachat/file-processing",
    summary="Загрузка файла и выбор операции",
    description="",
    tags=["Работа с GigaChat"],
)
async def file_processing(
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
        None,
        description="Альтернатива температуре (необязательное, https://developers.sber.ru/docs/ru/gigachat/api/reference-grpc)",
    ),
) -> JSONResponse:

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

    result = await choice_action(
        file, action, percent_compress, custom_promt, temperature, top_p, None
    )

    if action == "compress":
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

    elif action == "tests":
        return json.loads(result)


@gigachat_router.post(
    "/api/gigachat/simple-chat",
    summary="Обычный диалог",
    description="",
    tags=["Работа с GigaChat"],
)
async def file_processing(
    message: str = Query(..., description="Сообщение GigaChat-у"),
    custom_promt: Optional[str] = Query(
        None, description="Свой промт (необязательное)"
    ),
    temperature: Optional[float] = Query(
        None, description="Температура модели (необязательное)"
    ),
    top_p: Optional[float] = Query(
        None,
        description="Альтернатива температуре (необязательное, https://developers.sber.ru/docs/ru/gigachat/api/reference-grpc)",
    ),
) -> JSONResponse:

    if message.strip() == "":
        return JSONResponse(status_code=400, content={"message": "Введите сообщение!"})

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

    result = await choice_action(
        None, "dialog", None, custom_promt, temperature, top_p, message
    )
    return {"answer": result}


@gigachat_router.post("/get-author-info/{book_id}")
async def fetch_author_info(book_id: str):
    book = await book_repo.get_book_by_id(book_id)
    if not book:
        return {"error": "Книга не найдена"}

    # Получаем текст книги для использования в запросе
    book_text = book.description  # Или любое другое поле, содержащее текст книги
    author_info = await get_author_info(book.title, book.author, book_text)

    await book_repo.update_book_info(book_id, author_info)

    return {
        "message": "Информация об авторе успешно обновлена",
        "author_info": author_info,
    }
=======
@gigachat_router.post("/api/gigachat/file-processing", summary="Загрузка файла и выбор операции", description="",
                      tags=["Работа с GigaChat"])
async def file_processing(
  file: UploadFile = File(..., media_type="application/pdf", description="Книга в формате PDF"),
  action: Literal["compress", "tests"] = Query("compress", description="Действие: сжать текст или сгенерировать тесты"),
  percent_compress: Optional[int] = Query(50, description="На сколько % сжать текст"),
  custom_promt: Optional[str] = Query(None, description="Свой промт (необязательное)"),
  temperature: Optional[float] = Query(None, description="Температура модели (необязательное)"),
  top_p: Optional[float] = Query(None, description="Альтернатива температуре (необязательное, https://developers.sber.ru/docs/ru/gigachat/api/reference-grpc)")) -> JSONResponse:

  # Проверка формата файла
  if not file.filename.endswith('.pdf'):
      raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

  # Проверка значений
  if action not in ["compress", "tests"]:
      return JSONResponse(status_code=400, content={"message": "Invalid action"})
  
  if not (10 <= percent_compress <= 90):
      return JSONResponse(status_code=400, content={"message": "Процент сжатия должен быть от 10 до 90 процентов!"})
  
  if temperature is not None and not (0 <= temperature <= 2):
      return JSONResponse(status_code=400, content={"message": "Значение температуры должно быть от 0 до 2!"})
  
  if top_p is not None and not (0 <= top_p <= 2):
      return JSONResponse(status_code=400, content={"message": "Значение top_p должно быть от 0 до 2!"})
  
  result = await choice_action(file, action, percent_compress, custom_promt, temperature, top_p, None)
  
  if action == 'compress':
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
  
  elif action == 'tests':
    return json.loads(result)
    

@gigachat_router.post("/api/gigachat/simple-chat", summary="Обычный диалог", description="",
                      tags=["Работа с GigaChat"])
async def file_processing(
  message: str = Query(..., description="Сообщение GigaChat-у"),
  custom_promt: Optional[str] = Query(None, description="Свой промт (необязательное)"),
  temperature: Optional[float] = Query(None, description="Температура модели (необязательное)"),
  top_p: Optional[float] = Query(None, description="Альтернатива температуре (необязательное, https://developers.sber.ru/docs/ru/gigachat/api/reference-grpc)")) -> JSONResponse:

  if message.strip() == "":
    return JSONResponse(status_code=400, content={"message": "Введите сообщение!"})

  if temperature is not None and not (0 <= temperature <= 2):
    return JSONResponse(status_code=400, content={"message": "Значение температуры должно быть от 0 до 2!"})
      
  if top_p is not None and not (0 <= top_p <= 2):
    return JSONResponse(status_code=400, content={"message": "Значение top_p должно быть от 0 до 2!"})
  
  result = await choice_action(None, "dialog", None, custom_promt, temperature, top_p, message)
  return {"answer": result}
>>>>>>> origin/backend_python
