import chardet
import os
import re

def detect_encoding(file_path: str) -> str:
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result: dict = chardet.detect(raw_data)
    return result['encoding']

def split_large_chapters(text, max_length=12000):
    chapters = []
    while len(text) > max_length:
        split_point = text.rfind(' ', 0, max_length)
        if split_point == -1:
            split_point = max_length
        chapters.append(text[:split_point])
        text = text[split_point:]
    chapters.append(text)
    return chapters

def split_book_by_chapters(file_path):
    # Проверяем, что файл существует
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")

    encoding = detect_encoding(file_path)
    chapters = []
    current_chapter = []

    # Определяем паттерны для глав
    ancient_numbers = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ", "Ⅺ", "Ⅻ"]
    modern_symbols = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "§"]
    chapter_patterns = ancient_numbers + modern_symbols + ["Глава", "Параграф"]

    # Компилируем регулярное выражение для поиска начала главы
    chapter_regex = re.compile(r'^\s*(?:' + '|'.join(chapter_patterns) + r')\b', re.IGNORECASE)

    with open(file_path, 'r', encoding=encoding) as file:
        for line in file:
            # Проверяем, является ли строка началом новой главы
            if chapter_regex.match(line.strip()):
                if current_chapter:
                    chapters.append(''.join(current_chapter))
                    current_chapter = []
            current_chapter.append(line)

        # Добавляем последнюю главу, если она есть
        if current_chapter:
            chapters.append(''.join(current_chapter))

    # Если главы не найдены, разбиваем текст на большие части
    if not chapters:
        with open(file_path, 'r', encoding=encoding) as file:
            text = file.read()
        chapters = split_large_chapters(text, max_length=12000)

    return chapters

def split_chapters(chapters, book_reader, database, id_book):
    book_reader.number_chapter = 0
    while book_reader.number_chapter < len(chapters):
        book_reader.number_chapter = book_reader.reading(chapters, book_reader.number_chapter)
        id_block = database.new_block()
        database.add_original_text(book_reader.data, id_block)
        database.add_id_book(id_block, id_book)
        book_reader.data = ""
