import re
from typing import List, Optional
from bson import ObjectId
from PyPDF2 import PdfReader
from models.BookText import BookText
from models.Book import Book
from models.TextBlock import TextBlock
from Utils.Fb2Processor import Fb2Processor  # Предполагается, что вы уже адаптировали Fb2Processor

class BookProcessor:
    def __init__(self, file_path: str, name_file: str):
        self.file_path = file_path
        self.name_file = name_file

    def read_text_file(self) -> str:
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def read_pdf_file(self) -> str:
        text_content = []
        with open(self.file_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        return "\n".join(text_content)

    def read_fb2_file(self) -> BookText:
        fb2_processor = Fb2Processor(self.file_path)
        return fb2_processor.extract_book_text()

    def get_chapters(self, file_type: str) -> List[str]:
        if file_type == "text/plain":
            content = self.read_text_file()
        elif file_type == "application/pdf":
            content = self.read_pdf_file()
        elif file_type == "application/fb2+xml":
            content = self.read_fb2_file().content
        else:
            raise ValueError("Unsupported file type")

        # Разделяем на главы по шаблону "(Глава|Часть)\s+\d+"
        chapters = re.split(r"(Глава|Часть)\s+\d+", content, flags=re.IGNORECASE)
        # Фильтруем пустые строки и пробелы
        chapters = [ch.strip() for ch in chapters if ch.strip()]
        return chapters

    def get_book(self, file_type: str) -> Book:
        if file_type == "text/plain":
            content = self.read_text_file()
            book_text = BookText(
                title=self.extract_line_content(content, "Title:") or "Название не указано",
                authors=self.extract_line_content(content, "Author(s):") or "Автор книги не указан",
                content=self.extract_line_content(content, "Content:") or "Описание отсутствует",
                annotation=None
            )
        elif file_type == "application/pdf":
            text = self.read_pdf_file()
            book_text = BookText(
                title="Неизвестно",
                authors="Неизвестно",
                content=text,
                annotation=None
            )
        elif file_type == "application/fb2+xml":
            book_text = self.read_fb2_file()
        else:
            raise ValueError("Unsupported file type")

        id_book = str(ObjectId())
        return Book(
        idBook=id_book,
        title=book_text.title,
        author=book_text.authors,
        description=book_text.content,
        annotation=book_text.annotation,
        status="reading",
        mode="default",
        nameFile=self.name_file,
        filePath=self.file_path,
        compressionLevel=0
    )

    def extract_line_content(self, content: str, prefix: str) -> Optional[str]:
        pattern = re.compile(prefix + r"\s*(.*)", re.IGNORECASE)
        match = pattern.search(content)
        if match:
            return match.group(1).strip()
        return None

    def divide_chapter_into_blocks(self, chapter: str, block_size: int = 1000) -> List[str]:
        blocks = []
        start_index = 0
        while start_index < len(chapter):
            end_index = min(start_index + block_size, len(chapter))
            blocks.append(chapter[start_index:end_index])
            start_index = end_index
        return blocks

    def process_chapters_and_blocks(self, chapters: List[str]) -> List[TextBlock]:
        text_blocks = []
        for chapter_index, chapter_content in enumerate(chapters):
            blocks = self.divide_chapter_into_blocks(chapter_content)
            for block_content in blocks:
                text_block = TextBlock(
                    _id=str(ObjectId()),
                    original=block_content,
                    numberChapter=chapter_index + 1
                )
                text_blocks.append(text_block)
        return text_blocks
