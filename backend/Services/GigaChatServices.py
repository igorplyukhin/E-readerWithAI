from typing import Literal, Optional
from fastapi import UploadFile
from fastapi.responses import JSONResponse
import requests
import uuid
from PyPDF2 import PdfReader
import io
<<<<<<< HEAD
from utils.ReadSettings import get_setting
=======
from Utils.ReadSettings import get_setting
>>>>>>> origin/backend_python

# Константы для авторизации и адресов
TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
AUTHORIZATION_HEADER = "Basic " + get_setting("BearerToken")
<<<<<<< HEAD
MAX_GIGACHAT_TOKENS = 4096  # Предположительно, максимальная длина ответа в токенах
=======
MAX_GIGACHAT_TOKENS = 4096 # Предположительно, максимальная длина ответа в токенах
>>>>>>> origin/backend_python

# Глобальная переменная для токена авторизации
auth_token = None


# Основная функция для обработки PDF и выбора действия
<<<<<<< HEAD
async def choice_action(
    file: Optional[UploadFile],
    action: Literal["compress", "tests", "dialog"],
    percent_compress: int,
    prompt: Optional[str],
    temperature: Optional[float],
    top_p: Optional[float],
    message: Optional[str],
):
    # Получаем токен
    get_token()
    if not auth_token:
        return JSONResponse(
            status_code=401, content={"message": "Не удалось получить токен."}
        )

    if action == "compress":
=======
async def choice_action(file: Optional[UploadFile], action: Literal['compress', 'tests', "dialog"], 
                        percent_compress: int, prompt: Optional[str], temperature: Optional[float], 
                        top_p: Optional[float], message: Optional[str]):
    # Получаем токен
    get_token()
    if not auth_token:
        return JSONResponse(status_code=401, content={"message": "Не удалось получить токен."})

    if action == 'compress':
>>>>>>> origin/backend_python
        # Загружаем PDF и разбиваем на блоки по 4000 символов
        pdf_bytes = await file.read()
        pdf_stream = io.BytesIO(pdf_bytes)
        blocks = load_and_chunk_pdf(pdf_stream, chunk_size=2500)

        # Итоговый сжатый текст
        final_compressed_text = ""

        for i, block in enumerate(blocks):
            print(f"\nСжимаем блок {i + 1} из {len(blocks)}...")
<<<<<<< HEAD
            compressed_text = compress_block_with_retry(
                block, percent_compress, 2, prompt, temperature, top_p
            )
            if compressed_text:
                final_compressed_text += compressed_text + "\n\n"

=======
            compressed_text = compress_block_with_retry(block, percent_compress, 2, prompt, temperature, top_p)
            if compressed_text:
                final_compressed_text += compressed_text + "\n\n"
        
>>>>>>> origin/backend_python
        # Вывод итогового сжатого текста
        print("\nИтоговый сжатый текст для всех блоков:")
        print(final_compressed_text)
        return final_compressed_text
<<<<<<< HEAD

    elif action == "tests":
=======
    
    elif action == 'tests':
>>>>>>> origin/backend_python
        # Загружаем PDF и разбиваем на блоки по 4000 символов
        pdf_bytes = await file.read()
        pdf_stream = io.BytesIO(pdf_bytes)
        blocks = load_and_chunk_pdf(pdf_stream, chunk_size=2500)

        if prompt == None or prompt == "":
<<<<<<< HEAD
            prompt = (
                f"Запрос: Необходимо проверить читателя на понимание текста."
                f"Составь 5 вопросов полностью на русском языке по фрагменту текста, которые проверят понимание читателя фрагмента текста."
                f"Напиши каждый вопрос и 4 варианта ответа на каждый вопрос, где только 1 верный, укажи только номер ответа который является верным.###"
                f"Формат вывода:"
                f"""{{"questions":[{{"question":"Вопрос 1?","answers":[{{"text":"1. Ответ 1","is_correct":false}},{{"text":"2. Ответ 2","is_correct":true}},{{"text":"3. Ответ 3","is_correct":false}},{{"text":"4. Ответ 4","is_correct":false}}]}},{{"question":"Вопрос 2?","answers":[{{"text":"1. Ответ 1","is_correct":true}},{{"text":"2. Ответ 2","is_correct":false}},{{"text":"3. Ответ 3","is_correct":false}},{{"text":"4. Ответ 4","is_correct":false}}]}},{{"question":"Вопрос 3?","answers":[{{"text":"1. Ответ 1","is_correct":false}},{{"text":"2. Ответ 2","is_correct":false}},{{"text":"3. Ответ 3","is_correct":true}},{{"text":"4. Ответ 4","is_correct":false}}]}},{{"question":"Вопрос 4?","answers":[{{"text":"1. Ответ 1","is_correct":false}},{{"text":"2. Ответ 2","is_correct":false}},{{"text":"3. Ответ 3","is_correct":false}},{{"text":"4. Ответ 4","is_correct":true}}]}},{{"question":"Вопрос 5?","answers":[{{"text":"1. Ответ 1","is_correct":false}},{{"text":"2. Ответ 2","is_correct":true}},{{"text":"3. Ответ 3","is_correct":false}},{{"text":"4. Ответ 4","is_correct":false}}]}}]}}"""
                f'{{"Question": "Вопрос 1?", "answers": [ "Ответ 1",  "Ответ 2", "Ответ 3", "Ответ 4" ], "correct_answer": "номер верного ответа"}}'
                f"Напиши только эту информацию, ничего лишнего. Не повторяйся."
                f"Исходный текст: \n{blocks}"
            )
        result = send_to_gigachat(prompt, "5", temperature, top_p)
        print(result)
        return result

    elif action == "dialog":
=======
          prompt = (
            f"Запрос: Необходимо проверить читателя на понимание текста."
            f"Составь 5 вопросов полностью на русском языке по фрагменту текста, которые проверят понимание читателя фрагмента текста."
            f"Напиши каждый вопрос и 4 варианта ответа на каждый вопрос, где только 1 верный, укажи только номер ответа который является верным.###"
            f"Формат вывода:"
            f'''{{"questions":[{{"question":"Вопрос 1?","answers":[{{"text":"1. Ответ 1","is_correct":false}},{{"text":"2. Ответ 2","is_correct":true}},{{"text":"3. Ответ 3","is_correct":false}},{{"text":"4. Ответ 4","is_correct":false}}]}},{{"question":"Вопрос 2?","answers":[{{"text":"1. Ответ 1","is_correct":true}},{{"text":"2. Ответ 2","is_correct":false}},{{"text":"3. Ответ 3","is_correct":false}},{{"text":"4. Ответ 4","is_correct":false}}]}},{{"question":"Вопрос 3?","answers":[{{"text":"1. Ответ 1","is_correct":false}},{{"text":"2. Ответ 2","is_correct":false}},{{"text":"3. Ответ 3","is_correct":true}},{{"text":"4. Ответ 4","is_correct":false}}]}},{{"question":"Вопрос 4?","answers":[{{"text":"1. Ответ 1","is_correct":false}},{{"text":"2. Ответ 2","is_correct":false}},{{"text":"3. Ответ 3","is_correct":false}},{{"text":"4. Ответ 4","is_correct":true}}]}},{{"question":"Вопрос 5?","answers":[{{"text":"1. Ответ 1","is_correct":false}},{{"text":"2. Ответ 2","is_correct":true}},{{"text":"3. Ответ 3","is_correct":false}},{{"text":"4. Ответ 4","is_correct":false}}]}}]}}'''
            f'{{"Question": "Вопрос 1?", "answers": [ "Ответ 1",  "Ответ 2", "Ответ 3", "Ответ 4" ], "correct_answer": "номер верного ответа"}}'
            f"Напиши только эту информацию, ничего лишнего. Не повторяйся."
            f"Исходный текст: \n{blocks}"
          )
        result = send_to_gigachat(prompt, "5", temperature, top_p)
        print(result)
        return result
    
    elif action == 'dialog':
>>>>>>> origin/backend_python
        if prompt == None or prompt == "":
            prompt = "Ты эмпатичный книголюб. Общайся с пользователем и помогаем ему разобраться с его вопросами."
        result = send_to_gigachat(prompt, message, temperature, top_p)
        print(result)
        return result

<<<<<<< HEAD
=======
    
>>>>>>> origin/backend_python

# Функция для получения токена доступа
def get_token(scope="GIGACHAT_API_CORP"):
    global auth_token
    rq_uid = str(uuid.uuid4())
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": rq_uid,
<<<<<<< HEAD
        "Authorization": AUTHORIZATION_HEADER,
=======
        "Authorization": AUTHORIZATION_HEADER
>>>>>>> origin/backend_python
    }
    payload = f"scope={scope}"
    try:
        response = requests.post(TOKEN_URL, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            json_response = response.json()
            auth_token = json_response.get("access_token")
            print("Токен успешно получен.")
        else:
<<<<<<< HEAD
            print(
                "Не удалось получить токен доступа:",
                response.status_code,
                response.text,
            )
=======
            print("Не удалось получить токен доступа:", response.status_code, response.text)
>>>>>>> origin/backend_python
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе токена доступа: {e}")


<<<<<<< HEAD
=======

>>>>>>> origin/backend_python
# Функция для отправки сообщения в GigaChat
def send_to_gigachat(prompt, message, temperature=0.87, top_p=0.47) -> str:
    if not auth_token:
        print("Ошибка: Токен не получен. Пожалуйста, проверьте авторизацию.")
        return None
<<<<<<< HEAD

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
=======
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
>>>>>>> origin/backend_python
    }
    payload = {
        "model": "GigaChat-Max:latest",
        "messages": [
            {"role": "system", "content": prompt},
<<<<<<< HEAD
            {"role": "user", "content": message},
=======
            {"role": "user", "content": message}
>>>>>>> origin/backend_python
        ],
        "temperature": temperature,
        "top_p": top_p,
        "n": 1,
        "stream": False,
        "max_tokens": MAX_GIGACHAT_TOKENS,
        "repetition_penalty": 1.07,
        "update_interval": 0,
<<<<<<< HEAD
        "function_call": "auto",
    }

=======
        "function_call": "auto"
    }
    
>>>>>>> origin/backend_python
    try:
        response = requests.post(CHAT_URL, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            json_response = response.json()
            choices = json_response.get("choices")
            if choices:
                compressed_content = choices[0].get("message", {}).get("content")
                return compressed_content
            else:
                print("Не удалось получить содержимое ответа.")
                return None
        else:
<<<<<<< HEAD
            print(
                "Ошибка при отправке в GigaChat:", response.status_code, response.text
            )
=======
            print("Ошибка при отправке в GigaChat:", response.status_code, response.text)
>>>>>>> origin/backend_python
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса в GigaChat API: {e}")
        return None


<<<<<<< HEAD
=======

>>>>>>> origin/backend_python
# Функция для загрузки и разбиения PDF на чанки с учетом завершенности предложений и абзацев
def load_and_chunk_pdf(pdf_stream: io.BytesIO, chunk_size=1000):
    print(pdf_stream)
    reader = PdfReader(pdf_stream)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n"
<<<<<<< HEAD

    text = " ".join(text.replace("\n", " ").replace("\r", "").split())
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

=======
    
    text = ' '.join(text.replace('\n', ' ').replace('\r', '').split())
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
>>>>>>> origin/backend_python
    print(f"Загружено {len(chunks)} чанков текста из PDF.")
    return chunks


<<<<<<< HEAD
# Функция для обработки и контроля сжатия блоков
def compress_block_with_retry(
    block, compression_rate, max_attempts, promt, temperature, top_p
):
    # target_length = int(len(block) * (1 - compression_rate / 100))
    target_min_length = int(
        len(block) - ((len(block)) * ((compression_rate + 20) / 100))
    )
    target_max_length = int(
        len(block) - ((len(block)) * ((compression_rate - 20) / 100))
    )
    attempt = 0
    best_result = None
    best_length_difference = float("inf")  # Разница между желаемой длиной и текущей

    while attempt < max_attempts:
        print(
            f"\nПопытка {attempt + 1} сжать блок до диапазона {target_min_length} - {target_max_length} символов..."
        )
        if promt == "" or promt == None:
            promt = (
                f"Сожми входной текст на указанное количество процентов от исходного размера, сохранив при этом исходный смысл и контекст."
                f"Если в тексте присутствуют формулы или определения, сохраняй их в исходном виде."
                f"Избегай излишней детализации, но постарайся сохранить логическую структуру и последовательность изложения."
                f"Рассмотри возможность использования таких методов, как обобщение текста, извлечение сущности или замена слов, чтобы уменьшить размер текста."
                f"Удаляй повторяющиеся и ненужные слова из следующего текста. Особое внимание удели канцеляризмам."
                f"Убедись, что объём сжатого текста от {target_min_length} до {target_max_length} символов в десятичной системе счисления.  Текст:\n{block}"
            )

        compressed_text = send_to_gigachat(
            promt, f"{compression_rate}%", temperature, top_p
        )

        if compressed_text:
            response_length = len(compressed_text)
            print(
                f"Длина ответа: {response_length} символов (ожидалось {target_min_length} - {target_max_length})."
            )

=======


# Функция для обработки и контроля сжатия блоков
def compress_block_with_retry(block, compression_rate, max_attempts, promt, temperature, top_p):
    #target_length = int(len(block) * (1 - compression_rate / 100))
    target_min_length = int(len(block) - ((len(block)) * ((compression_rate + 20) / 100)))
    target_max_length = int(len(block) - ((len(block)) * ((compression_rate - 20) / 100)))
    attempt = 0
    best_result = None
    best_length_difference = float('inf')  # Разница между желаемой длиной и текущей

    while attempt < max_attempts:
        print(f"\nПопытка {attempt + 1} сжать блок до диапазона {target_min_length} - {target_max_length} символов...")
        if promt == "" or promt == None:
          promt = (
              f"Сожми входной текст на указанное количество процентов от исходного размера, сохранив при этом исходный смысл и контекст."
              f"Если в тексте присутствуют формулы или определения, сохраняй их в исходном виде."
              f"Избегай излишней детализации, но постарайся сохранить логическую структуру и последовательность изложения."
              f"Рассмотри возможность использования таких методов, как обобщение текста, извлечение сущности или замена слов, чтобы уменьшить размер текста."
              f"Удаляй повторяющиеся и ненужные слова из следующего текста. Особое внимание удели канцеляризмам."
              f"Убедись, что объём сжатого текста от {target_min_length} до {target_max_length} символов в десятичной системе счисления.  Текст:\n{block}"
          )
        
        compressed_text = send_to_gigachat(promt, f"{compression_rate}%", temperature, top_p)
        
        if compressed_text:
            response_length = len(compressed_text)
            print(f"Длина ответа: {response_length} символов (ожидалось {target_min_length} - {target_max_length}).")
            
>>>>>>> origin/backend_python
            # Если длина ответа находится в пределах желаемого диапазона, сохраняем его и завершаем попытки
            if target_min_length <= response_length <= target_max_length:
                print("Ответ соответствует ожидаемому диапазону.")
                return f"\n" + compressed_text
<<<<<<< HEAD

=======
            
>>>>>>> origin/backend_python
            # Если это лучший результат по близости к целевой длине, сохраняем его
            length_difference = abs(response_length - target_min_length)
            if length_difference < best_length_difference:
                best_result = f"Фрагмент:       " + compressed_text
                best_length_difference = length_difference
<<<<<<< HEAD

=======
            
>>>>>>> origin/backend_python
            # Если ответ слишком короткий, увеличиваем сжатие, если длинный — уменьшаем
            print("Ответ не попал в диапазон. Повтор запроса с той же настройкой.")
        else:
            print("Ошибка при получении ответа от GigaChat.")
<<<<<<< HEAD

        attempt += 1

    return best_result  # Возвращаем лучший результат, если не удалось попасть в целевой диапазон


# Функция для узнавания автора книги
async def get_author_info(book_title: str, author_name: str, book_text: str) -> str:
    prompt = (
        f"Нужно узнать автора книги '{book_title}'. "
        f"Если в книге указаны сведения об авторе, используй их для ответа. "
        f"Если таких сведений нет, используй часть текста: '{book_text[:2000]}' для поиска автора. "
        f"Если не удается найти информацию, напиши, что автор неизвестен и не придумывай ответ."
    )
    result = send_to_gigachat(prompt, "", temperature=0.87, top_p=0.47)
    return result
=======
        
        attempt += 1

    return best_result  # Возвращаем лучший результат, если не удалось попасть в целевой диапазон
>>>>>>> origin/backend_python
