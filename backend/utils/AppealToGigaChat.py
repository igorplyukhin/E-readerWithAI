from typing import Literal, Optional
from click import prompt
from fastapi import UploadFile
from fastapi.responses import JSONResponse
import requests
import json
import uuid
from PyPDF2 import PdfReader
import io

# Константы для авторизации и адресов
TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
AUTHORIZATION_HEADER = "Basic ZTkxZjVmMGMtODQ0NS00ZTUwLWExY2QtYWJmMTJhMGY3MDVmOjE1NzJlMmE5LTc5ZmItNGVjMS04ZDJhLTMwNzE3NWQ2NjBmOA=="
MAX_GIGACHAT_TOKENS = 4096 # Предположительно, максимальная длина ответа в токенах

# Глобальная переменная для токена авторизации
auth_token = None


# Основная функция для обработки PDF и выбора действия
async def choice_action(file: UploadFile, action: Literal['compress', 'tests'], percent_compress: int,
                          prompt: Optional[str], temperature: Optional[float], top_p: Optional[float]):
    # Шаг 1: Получаем токен
    get_token()
    if not auth_token:
        return JSONResponse(status_code=401, content={"message": "Не удалось получить токен."})

    # Шаг 2: Загружаем PDF и разбиваем на блоки по 4000 символов
    pdf_bytes = await file.read()
    pdf_stream = io.BytesIO(pdf_bytes)
    blocks = load_and_chunk_pdf(pdf_stream, chunk_size=2500)

    # Итоговый сжатый текст
    final_compressed_text = ""

    if action == 'compress':
        for i, block in enumerate(blocks):
            print(f"\nСжимаем блок {i + 1} из {len(blocks)}...")
            compressed_text = compress_block_with_retry(block, percent_compress, 2, prompt, temperature, top_p)
            if compressed_text:
                final_compressed_text += compressed_text + "\n\n"
        
        # Вывод итогового сжатого текста
        print("\nИтоговый сжатый текст для всех блоков:")
        print(final_compressed_text)
        return final_compressed_text
    
    elif action == 'tests':
        if prompt == None or prompt == "":
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
          """ prompt = (
              f"Запрос: Необходимо проверить читателя на понимание текста."
              f"Составь 5 вопросов полностью на русском языке по фрагменту текста, которые проверят понимание читателя фрагмента текста."
              f"Напиши каждый вопрос и 4 варианта ответа на каждый вопрос, где только 1 верный, укажи только номер ответа который является верным.###"
              f"Формат вывода:"
              f"###"
              f'"Вопрос 1?"'
              f"1.Ответ 1 "
              f"2.Ответ 2 "
              f"3.Ответ 3 "
              f"4.Ответ 4 "
              f'"Ответ: номер верного ответа"'
              f"###"
              f'"Вопрос 2?"'
              f"1.Ответ 1 "
              f"2.Ответ 2 "
              f"3.Ответ 3 "
              f"4.Ответ 4 "
              f'"Ответ: номер верного ответа"'
              f"###"
              f"... (и так далее для 5)"
              f"Напиши только эту информацию, ничего лишнего. Не повторяйся."
              f"Исходный текст: \n{blocks}"
          ) """
        result = send_to_gigachat(prompt, "5", temperature, top_p)
        print(result)
        return {"number_of_chunks": len(blocks), "compress_text": result}

    

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
def send_to_gigachat(prompt, message, temperature=0.87, top_p=0.47):
    if not auth_token:
        print("Ошибка: Токен не получен. Пожалуйста, проверьте авторизацию.")
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
        "temperature": 0.87,
        "top_p": 0.47,
        "n": 1,
        "stream": False,
        "max_tokens": MAX_GIGACHAT_TOKENS,
        "repetition_penalty": 1.07,
        "update_interval": 0,
        "function_call": "auto"
    }
    
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
            print("Ошибка при отправке в GigaChat:", response.status_code, response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса в GigaChat API: {e}")
        return None



# Функция для загрузки и разбиения PDF на чанки с учетом завершенности предложений и абзацев
def load_and_chunk_pdf(pdf_stream: io.BytesIO, chunk_size=1000):
    print(pdf_stream)
    reader = PdfReader(pdf_stream)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n"
    
    text = ' '.join(text.replace('\n', ' ').replace('\r', '').split())
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    print(f"Загружено {len(chunks)} чанков текста из PDF.")
    return chunks




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
            
            # Если длина ответа находится в пределах желаемого диапазона, сохраняем его и завершаем попытки
            if target_min_length <= response_length <= target_max_length:
                print("Ответ соответствует ожидаемому диапазону.")
                return f"\n" + compressed_text
            
            # Если это лучший результат по близости к целевой длине, сохраняем его
            length_difference = abs(response_length - target_min_length)
            if length_difference < best_length_difference:
                best_result = f"Фрагмент:       " + compressed_text
                best_length_difference = length_difference
            
            # Если ответ слишком короткий, увеличиваем сжатие, если длинный — уменьшаем
            print("Ответ не попал в диапазон. Повтор запроса с той же настройкой.")
        else:
            print("Ошибка при получении ответа от GigaChat.")
        
        attempt += 1

    return best_result  # Возвращаем лучший результат, если не удалось попасть в целевой диапазон
