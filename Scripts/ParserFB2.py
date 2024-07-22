from lxml import etree
import chardet
import os


# Определение кодировки файла
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        return encoding


# Чтение fb2 файла и парсинг с помощью lxml
def parse_fb2(file_path):
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
    root = etree.fromstring(content.encode(encoding))
    return root


def extract_author(tree):
    author_element = tree.find('.//{http://www.gribuser.ru/xml/fictionbook/2.0}author')
    if author_element is not None:
        first_name = author_element.find(
            '{http://www.gribuser.ru/xml/fictionbook/2.0}first-name').text if author_element.find(
            '{http://www.gribuser.ru/xml/fictionbook/2.0}first-name') is not None else ''
        middle_name = author_element.find(
            '{http://www.gribuser.ru/xml/fictionbook/2.0}middle-name').text if author_element.find(
            '{http://www.gribuser.ru/xml/fictionbook/2.0}middle-name') is not None else ''
        last_name = author_element.find(
            '{http://www.gribuser.ru/xml/fictionbook/2.0}last-name').text if author_element.find(
            '{http://www.gribuser.ru/xml/fictionbook/2.0}last-name') is not None else ''
        full_name = f"{first_name} {middle_name} {last_name}".strip()
        return full_name
    return None


# Функция для извлечения текста книги
def extract_text(root):
    author = extract_author(root)
    title_info = root.find('.//{http://www.gribuser.ru/xml/fictionbook/2.0}title-info')
    book_title = title_info.find('.//{http://www.gribuser.ru/xml/fictionbook/2.0}book-title').text
    body = root.find('.//{http://www.gribuser.ru/xml/fictionbook/2.0}body')
    paragraphs = body.findall('.//{http://www.gribuser.ru/xml/fictionbook/2.0}p')

    text = ''
    for para in paragraphs:
        para_text = para.text
        if para_text is not None:
            text += para_text.strip() + '\n'

    return text, author, book_title


# Функция для обработки fb2 файла
def process_fb2(name_file):
    # Парсинг файла fb2
    tree = parse_fb2(name_file)
    encoding = detect_encoding(name_file)
    # Извлечение текста, автора и названия книги
    book_text, author, book_title = extract_text(tree)

    # Запись текста книги в файл TXT
    output_file = "fb2-txt.txt"
    with open(output_file, 'w', encoding=encoding) as f:
        f.write(book_text)
    return output_file

#
# fb2_file = "72963.fb2"
# name_file = process_fb2(fb2_file)
# print(open(name_file, "r", encoding="utf-8").read())
#
