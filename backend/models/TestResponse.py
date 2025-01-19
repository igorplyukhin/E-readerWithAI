from typing import List
from pydantic import BaseModel

class Answer(BaseModel):
    text: str  # Текст ответа
    is_correct: bool  # Флаг правильности ответа

class Question(BaseModel):
    question: str  # Вопрос
    answers: List[Answer]  # Список ответов

class TestResponse(BaseModel):
    questions: List[Question]  # Список вопросов

class MessageResponse(BaseModel):
    message: str