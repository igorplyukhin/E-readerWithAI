from typing import List, Literal, Optional
import requests
import uuid
from Utils.ReadSettings import get_setting
from Utils.TextUtils import split_into_blocks
import logging
import urllib3
from Repositories.BookRepository import BookRepository
from fastapi import HTTPException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Инициализация репозитория
book_repository = BookRepository()


# Константы для авторизации и адресов
TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
AUTHORIZATION_HEADER = "Basic " + get_setting("BearerToken")
MAX_GIGACHAT_TOKENS = 4096  # Максимальная длина ответа в токенах

# Глобальная переменная для токена авторизации
auth_token = None

async def choice_action(
    text_blocks: List[dict],
    action: Literal["compress", "tests"],
    percent_compress: int,
    prompt: Optional[str],
    temperature: Optional[float],
    top_p: Optional[float],
    book: dict,
    book_id: str,
):
    logging.info(f"Действие: {action}, Процент сжатия: {percent_compress}, ID книги: {book_id}")

    # Получаем токен
    get_token()
    if not auth_token:
        logging.error("Ошибка: Не удалось получить токен авторизации.")
        raise HTTPException(status_code=401, detail="Не удалось получить токен.")

    if action == "compress":
        # Проверяем, есть ли уже сжатый текст для указанного процента
        compressed_texts = book.get("compressedText", {})
        compression_key = str(percent_compress)

        if compression_key in compressed_texts and compressed_texts[compression_key]:
            logging.info(f"Сжатие на {percent_compress}% уже выполнено. Возвращаем сохраненные данные.")
            return compressed_texts[compression_key]

        logging.info("Сжатие выполняется впервые для данного процента.")
        text_contents = [
            block.get("original", "").replace("\n", " ").strip() for block in text_blocks if "original" in block
        ]
        full_text = " ".join(text_contents)
        logging.info(f"Объединение текстовых блоков. Общая длина текста: {len(full_text)} символов.")

        # Разбиваем текст на блоки по 2500 символов
        blocks_2500 = split_into_blocks(full_text, block_size=2500)
        logging.info(f"Текст разбит на {len(blocks_2500)} блоков по ~2500 символов.")

        # Сжимаем каждый блок
        compressed_blocks = []
        for i, block in enumerate(blocks_2500):
            logging.info(f"Сжимаем блок {i + 1}/{len(blocks_2500)} длиной {len(block)} символов...")
            compressed_text = compress_block_with_retry(block, percent_compress, 2, prompt, temperature, top_p)
            if compressed_text:
                logging.info(f"Блок {i + 1} успешно сжат. Новая длина: {len(compressed_text)} символов.")
                compressed_blocks.append(compressed_text)
            else:
                logging.warning(f"Блок {i + 1} не удалось сжать. Пропускаем...")

        if not compressed_blocks:
            logging.error("Не удалось сжать ни один блок. Завершение процесса.")
            raise HTTPException(status_code=500, detail="Сжатие текста завершилось неудачно.")

        # Объединяем сжатые блоки в единый текст
        full_compressed_text = " ".join(compressed_blocks)
        logging.info(f"Объединение всех сжатых блоков завершено. Длина объединенного текста: {len(full_compressed_text)} символов.")

        # Разбиваем объединённый текст на блоки по 1000 символов
        final_blocks = split_into_blocks(full_compressed_text, block_size=1000)
        logging.info(f"Сжатый текст разбит на {len(final_blocks)} блоков по ~1000 символов.")

        # Сохраняем блоки в коллекции и их IDs в книге
        compressed_block_ids = []
        for block in final_blocks:
            compressed_block_id = await book_repository.insert_compressed_block(
                book_id, percent_compress, block
            )
            compressed_block_ids.append(compressed_block_id)

        # Сохраняем IDs в compressedText
        book["compressedText"][compression_key] = compressed_block_ids
        await book_repository.update_book_field(book_id, "compressedText", book["compressedText"])

        logging.info(f"Сжатие на {percent_compress}% успешно сохранено в книге с ID: {book_id}.")
        logging.info(f"Итоговые длины блоков: {[len(block) for block in final_blocks]}")

        return compressed_block_ids

    elif action == "tests":
        logging.info("Начинается процесс генерации тестов...")
        text_contents = [
            block.get("original", "").replace("\n", " ").strip() for block in text_blocks if "original" in block
        ]
        full_text = " ".join(text_contents)
        logging.info(f"Объединение текстовых блоков для генерации тестов. Общая длина текста: {len(full_text)} символов.")

        if not prompt:
            prompt = (
                "Составь 5 вопросов на русском языке по тексту, которые проверят понимание читателя. "
                "Напиши 4 варианта ответа на каждый вопрос, укажи правильный ответ. "
            )
        result = send_to_gigachat(prompt, full_text, temperature, top_p)
        logging.info("Генерация тестов завершена успешно.")
        return result


# Функция для получения токена доступа
def get_token(scope="GIGACHAT_API_CORP"):
    global auth_token
    rq_uid = str(uuid.uuid4())
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": rq_uid,
        "Authorization": AUTHORIZATION_HEADER
    }
    payload = f"scope={scope}"
    try:
        response = requests.post(TOKEN_URL, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            json_response = response.json()
            auth_token = json_response.get("access_token")
            print("Токен успешно получен.")
        else:
            print("Не удалось получить токен доступа:", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе токена доступа: {e}")

# Функция для отправки сообщения в GigaChat
def send_to_gigachat(prompt, message, temperature=0.87, top_p=0.47) -> str:
    if not auth_token:
        logging.error("Ошибка: Токен не получен. Пожалуйста, проверьте авторизацию.")
        return None

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "GigaChat-Max:latest",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ],
        "temperature": temperature,
        "top_p": top_p,
        "n": 1,
        "stream": False,
        "max_tokens": MAX_GIGACHAT_TOKENS,
        "repetition_penalty": 1.07,
        "update_interval": 0,
        "function_call": "auto"
    }

    try:
        response = requests.post(CHAT_URL, headers=headers, json=payload, verify=False)
        logging.info(f"Запрос отправлен в GigaChat: {payload}")
        logging.info(f"HTTP статус: {response.status_code}")

        if response.status_code == 200:
            json_response = response.json()
            logging.info(f"Ответ GigaChat: {json_response}")
            choices = json_response.get("choices")
            if choices:
                return choices[0].get("message", {}).get("content")
            else:
                logging.error("Не удалось получить содержимое ответа GigaChat.")
                return None
        else:
            logging.error(f"Ошибка при отправке в GigaChat: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса в GigaChat API: {e}")
        return None


# Функция для обработки и контроля сжатия блоков
def compress_block_with_retry(block, compression_rate, max_attempts, prompt, temperature, top_p):
    target_min_length = int(len(block) * (1 - (compression_rate + 20) / 100))
    target_max_length = int(len(block) * (1 - (compression_rate - 20) / 100))
    attempt = 0

    best_result = None
    best_length_difference = float('inf')  # Инициализация переменной для отслеживания наилучшего результата

    while attempt < max_attempts:
        logging.info(
            f"\nПопытка {attempt + 1} сжать блок до диапазона {target_min_length} - {target_max_length} символов..."
        )

        # Устанавливаем дефолтный prompt, если пользовательский не предоставлен
        if not prompt:
            prompt = (
                f"Сожми входной текст на {compression_rate}% от исходного размера, сохранив при этом исходный смысл и контекст. "
                f"Если в тексте присутствуют формулы или определения, сохраняй их в исходном виде. "
                f"Избегай излишней детализации, но постарайся сохранить логическую структуру и последовательность изложения. "
                f"Удаляй повторяющиеся и ненужные слова из следующего текста. "
                f"Убедись, что длина сжатого текста от {target_min_length} до {target_max_length} символов. "
            )

        # Отправляем запрос в GigaChat
        compressed_text = send_to_gigachat(prompt, block, temperature, top_p)
        if compressed_text:
            response_length = len(compressed_text)
            logging.info(f"Длина ответа: {response_length} символов (ожидалось {target_min_length} - {target_max_length}).")

            # Если длина ответа попадает в нужный диапазон, возвращаем его
            if target_min_length <= response_length <= target_max_length:
                logging.info(f"Сжатие успешно: длина блока {response_length} символов.")
                return compressed_text

            # Если результат лучше предыдущего (ближе к диапазону), сохраняем его
            length_difference = abs(response_length - target_min_length)
            if length_difference < best_length_difference:
                best_result = compressed_text
                best_length_difference = length_difference
                logging.info(f"Новый лучший результат: длина {response_length} символов (разница {length_difference}).")
        else:
            logging.error("Не удалось получить ответ от GigaChat.")

        attempt += 1

    # Если не удалось попасть в диапазон, возвращаем лучший из результатов
    if best_result:
        logging.warning("Не удалось попасть в диапазон, возвращаем лучший из полученных результатов.")
        return best_result
    else:
        logging.error("Не удалось получить приемлемый результат за все попытки.")
        return None



