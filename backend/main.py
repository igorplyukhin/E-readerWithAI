import logging
from fastapi import FastAPI

from Routes.BookRoutes import book_router
from Routes.UserRoutes import user_router
from Routes.GigaChatRoutes import gigachat_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат вывода логов
    datefmt="%Y-%m-%d %H:%M:%S",  # Формат времени
)
logger = logging.getLogger(__name__)  # Создаем логгер

app = FastAPI()

# Подключаем маршруты
app.include_router(book_router)
app.include_router(user_router)
app.include_router(gigachat_router)

if __name__ == "__main__":
    import uvicorn
    logger.info("Запуск FastAPI приложения...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
