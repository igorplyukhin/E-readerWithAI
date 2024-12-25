from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from Repositories.BookRepository import BookRepository
<<<<<<< HEAD
from utils.BookProcessor import BookProcessor
from utils.Fb2Processor import Fb2Processor
from Services.GigaChatServices import get_author_info

=======
from Utils.BookProcessor import BookProcessor
from Utils.Fb2Processor import Fb2Processor
>>>>>>> origin/backend_python

class BookService:
    def __init__(self):
        self.book_repository = BookRepository()

    async def process_uploaded_book(self, file_path: str, file_name: str, user_id: str):
        # Определяем тип файла
        file_type = self.get_supported_file_type(file_name)

        # Читаем и обрабатываем файл
        if file_type == "application/pdf":
            book_processor = BookProcessor(file_path, file_name)
            book_text = book_processor.read_pdf_file()
        elif file_type == "application/fb2+xml":
            fb2_processor = Fb2Processor(file_path)
            book_text = fb2_processor.extract_book_text()
        elif file_type == "text/plain":
            book_processor = BookProcessor(file_path, file_name)
            book_text = book_processor.read_text_file()
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type")

        if not book_text:
            raise HTTPException(status_code=500, detail="Error processing file")

        # Получаем структуру книги и текстовые блоки
        book_processor = BookProcessor(file_path, file_name)
        book = book_processor.get_book(file_type)
        chapters = book_processor.get_chapters(file_type)
        text_blocks = book_processor.process_chapters_and_blocks(chapters)

        # Сериализуем книгу и вставляем в базу данных
        book_dict = jsonable_encoder(book)
        book_id = await self.book_repository.insert_book(book_dict)
        book_dict["_id"] = book_id  # Заменяем ObjectId на строку

        # Сериализуем и вставляем text_blocks
        text_block_documents = jsonable_encoder(text_blocks)
<<<<<<< HEAD
        text_block_ids = await self.book_repository.insert_text_blocks(
            text_block_documents
        )
=======
        text_block_ids = await self.book_repository.insert_text_blocks(text_block_documents)
>>>>>>> origin/backend_python

        # Обновляем книгу с textBlockIds
        await self.book_repository.update_book_text_block_ids(book_id, text_block_ids)

        # Обновляем пользователя
        await self.book_repository.update_user_books(user_id, book_id)

<<<<<<< HEAD
        author_info = await get_author_info(
            book_dict["title"], book_dict["authors"], book_dict["annotation"] or ""
        )
        print(author_info)  # Здесь получаем информацию об авторе

        # Сохранение информации об авторе в MongoDB
        await BookService.book_repository.update_book_info(
            book_dict["idBook"], author_info
        )

        return book_dict

    def get_supported_file_type(self, file_name: str) -> str:
        extension = file_name.split(".")[-1].lower()
        return {
            "pdf": "application/pdf",
            "fb2": "application/fb2+xml",
            "txt": "text/plain",
=======
        return book_dict

    def get_supported_file_type(self, file_name: str) -> str:
        extension = file_name.split('.')[-1].lower()
        return {
            "pdf": "application/pdf",
            "fb2": "application/fb2+xml",
            "txt": "text/plain"
>>>>>>> origin/backend_python
        }.get(extension)
