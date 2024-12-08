from fastapi import FastAPI, File, Query, UploadFile, Form, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal, Optional
from utils.AppealToGigaChat import choice_action
import json


app = FastAPI()
gigachat_router = APIRouter()

class InputData(BaseModel):
    action: Literal["compress", "tests"]
    number: int

@gigachat_router.post("/appendToGigachat/", summary="Загрузка файла и выбор операции", description="",
                      tags=["Работа с GigaChat"])
async def upload_file(
    file: UploadFile = File(..., media_type="application/pdf", description="Книга в формате PDF"),
    action: Literal["compress", "tests"] = Query("compress", description="Действие: сжать текст или сгенерировать тесты"),
    percent_compress: Optional[int] = Query(50, description="На сколько % сжать текст"),
    custom_promt: Optional[str] = Query(None, description="Свой промт (необязательное)"),
    temperature: Optional[float] = Query(None, description="Температура модели (необязательное)"),
    top_p: Optional[float] = Query(None, description="Альтернатива температуре (необязательное, https://developers.sber.ru/docs/ru/gigachat/api/reference-grpc)")):

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
    
    # Здесь можно добавить логику работы с файлом
    result = await choice_action(file, action, percent_compress, custom_promt, temperature, top_p)
    
    if action == 'compress':
      return {"compress_text": result}
    elif action == 'tests':
      return json.loads(result)