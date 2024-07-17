import chardet
import re


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
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
    page_break = '\f'
    ancient_numbers = list("ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ")
    modern_symbols = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV",
                      "§"]
    encoding = detect_encoding(file_path)
    chapters = []
    current_chapter = []

    chapter_patterns = ancient_numbers + modern_symbols + [r"Глава", r"Параграф"]
    chapter_regex = re.compile(r'|'.join(map(lambda x: fr"(^\s*{x}\s*)", chapter_patterns)))

    with open(file_path, 'r', encoding=encoding) as file:
        for line in file:
            if chapter_regex.match(line.strip()):
                if current_chapter:
                    chapters.append(''.join(current_chapter))
                    current_chapter = []
            if page_break in line:
                if current_chapter:
                    current_chapter.append(line.replace(page_break, ''))
                    chapters.append(''.join(current_chapter))
                    current_chapter = []
            else:
                current_chapter.append(line)
        if current_chapter:
            chapters.append(''.join(current_chapter))

    if not chapters:
        with open(file_path, 'r', encoding=encoding) as file:
            text = file.read()
        chapters = split_large_chapters(text, max_length=12000)

    return chapters