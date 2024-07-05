import chardet
import re

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def split_book_by_chapters(file_path, ancient_numbers, modern_symbols, page_break='\f'):
    encoding = detect_encoding(file_path)
    chapters = []
    current_chapter = []

    # Создаем регулярное выражение для всех чисел и ключевых слов
    chapter_patterns = ancient_numbers + modern_symbols + [r"Глава", r"Параграф", r"\d+\."]
    chapter_regex = re.compile(r'|'.join(map(lambda x: fr"(^\s*{x}\s*)", chapter_patterns)))

    with open(file_path, 'r', encoding=encoding) as file:
        for line in file:
            # Проверка на заголовок главы
            if chapter_regex.match(line.strip()):
                if current_chapter:
                    chapters.append(''.join(current_chapter))
                    current_chapter = []
            # Проверка на разрыв страницы
            if page_break in line:
                if current_chapter:
                    current_chapter.append(line.replace(page_break, ''))
                    chapters.append(''.join(current_chapter))
                    current_chapter = []
            else:
                current_chapter.append(line)
        # Добавляем последнюю главу, если она существует
        if current_chapter:
            chapters.append(''.join(current_chapter))
    return chapters

# Пример использования
file_path = 'book.txt'
ancient_numbers = list("ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ")
modern_symbols = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "§"]
chapters = split_book_by_chapters(file_path, ancient_numbers, modern_symbols, page_break='\f')

# Вывод глав
for i, chapter in enumerate(chapters, 1):
    print(f"Глава {i}")
    print(chapter[:1000])  # выводим первые 1000 символов главы
    print("\n" + "-"*50 + "\n")
