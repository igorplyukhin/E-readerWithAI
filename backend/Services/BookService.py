from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from Repositories.BookRepository import BookRepository
from Utils.BookProcessor import BookProcessor
from Utils.Fb2Processor import Fb2Processor
from bson import ObjectId
from pymongo.results import UpdateResult

class BookService:
    def __init__(self):
        self.book_repository = BookRepository()

    async def process_uploaded_book(self, file_path: str, file_name: str, user_id: str):
        try:
            file_type = self.get_supported_file_type(file_name)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error detecting file type")

        if not file_type:
            raise HTTPException(status_code=415, detail="Unsupported file type")

        try:
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
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error processing file")

        if not book_text:
            raise HTTPException(status_code=500, detail="Processed book text is empty")

        try:
            book_processor = BookProcessor(file_path, file_name)
            book = book_processor.get_book(file_type)
            chapters = book_processor.get_chapters(file_type)
            text_blocks = book_processor.process_chapters_and_blocks(chapters)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error generating book structure")

        try:
            book_dict = jsonable_encoder(book)
            book_id = await self.book_repository.insert_book(book_dict)
            book_dict["_id"] = str(book_id)  
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error inserting book into database")

        try:
            text_block_documents = jsonable_encoder(text_blocks)
            text_block_ids = await self.book_repository.insert_text_blocks(text_block_documents)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error inserting text blocks into database")

        try:
            await self.book_repository.update_book_text_block_ids(book_id, text_block_ids)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error updating book with text block IDs")

        try:
            await self.book_repository.update_user_books(user_id, book_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error updating user books")

        return book_dict

    def get_supported_file_type(self, file_name: str) -> str:
        extension = file_name.split('.')[-1].lower()
        return {
            "pdf": "application/pdf",
            "fb2": "application/fb2+xml",
            "txt": "text/plain"
        }.get(extension)
