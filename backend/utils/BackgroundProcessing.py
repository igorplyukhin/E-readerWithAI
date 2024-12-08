import asyncio
from pymongo import MongoClient
from bson import ObjectId
from pymongo.collection import ReturnDocument
from typing import List, Tuple

# Assuming the existence of these classes based on the Kotlin code
from models.Book import Book
from models.TextBlock import TextBlock
from utils.BookProcessor import BookProcessor
from utils.DatabaseFactory import DatabaseFactory

class BackgroundProcessing:

    @staticmethod
    async def process_book_in_background(idUser: str, filePath: str, nameFile: str, fileType: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, BackgroundProcessing._process_book_sync, idUser, filePath, nameFile, fileType)

    @staticmethod
    def _process_book_sync(idUser: str, filePath: str, nameFile: str, fileType: str):
        book_processor = BookProcessor(filePath, nameFile)
        chapters = book_processor.get_chapters(fileType)
        book = book_processor.get_book(fileType)

        books_collection = DatabaseFactory.get_books_collection()
        books_collection.insert_one(book.to_document())

        book_id = book.id_book

        users_collection = DatabaseFactory.get_users_collection()
        users_collection.update_one(
            {"_id": idUser},
            {"$addToSet": {"bookIds": book_id}}
        )

        text_blocks = []
        for chapter_index, chapter in enumerate(chapters):
            blocks = book_processor.divide_chapter_into_blocks(chapter)
            for block in blocks:
                text_block = TextBlock(
                    _id=str(ObjectId()),
                    original=block,
                    number_chapter=chapter_index + 1
                )
                text_blocks.append(text_block.to_document())

                books_collection.update_one(
                    {"_id": book_id},
                    {"$push": {"textBlockIds": text_block._id}}
                )

        text_blocks_collection = DatabaseFactory.get_text_blocks_collection()
        if text_blocks:
            text_blocks_collection.insert_many(text_blocks)

        books_collection.update_one(
            {"_id": book_id},
            {"$set": {"status": "ready"}}
        )

    @staticmethod
    async def process_summarization_for_block(text_block: TextBlock, mode: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, BackgroundProcessing._process_block_summarization_sync, text_block, mode)

    @staticmethod
    def _process_block_summarization_sync(text_block: TextBlock, mode: str):
        text_blocks_collection = DatabaseFactory.get_text_blocks_collection()
        if mode == "summarization":
            summarized_text = BackgroundProcessing.summarize_text(text_block.original)
        elif mode == "summarization_time":
            summarized_text = BackgroundProcessing.summarize_text_with_time(text_block.original)
        else:
            summarized_text = text_block.original

        update_field = "summary" if mode == "summarization" else "summaryTime"
        text_blocks_collection.update_one(
            {"_id": text_block._id},
            {"$set": {update_field: summarized_text}}
        )

    @staticmethod
    async def process_summarization_mode(book: Book, mode: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, BackgroundProcessing._process_summarization_mode_sync, book, mode)

    @staticmethod
    def _process_summarization_mode_sync(book: Book, mode: str):
        text_blocks_collection = DatabaseFactory.get_text_blocks_collection()
        blocks_cursor = text_blocks_collection.find({"_id": {"$in": book.textBlockIds}})
        blocks = [TextBlock.from_document(doc) for doc in blocks_cursor]

        for block in blocks:
            if mode == "summarization":
                summarized_text = BackgroundProcessing.summarize_text(block.original)
            elif mode == "summarization_time":
                summarized_text = BackgroundProcessing.summarize_text_with_time(block.original)
            else:
                summarized_text = block.original

            update_field = "summary" if mode == "summarization" else "summaryTime"
            text_blocks_collection.update_one(
                {"_id": block._id},
                {"$set": {update_field: summarized_text}}
            )

        books_collection = DatabaseFactory.get_books_collection()
        books_collection.update_one(
            {"_id": book.id_book},
            {"$set": {"status": "summarized"}}
        )

    @staticmethod
    def summarize_text(text: str) -> str:
        return "Суммированный текст"

    @staticmethod
    def summarize_text_with_time(text: str) -> str:
        return "Суммированный текст с учетом времени"

    @staticmethod
    def generate_questions_for_block(text: str) -> Tuple[List[str], List[str]]:
        questions = ["Вопрос 1 по блоку", "Вопрос 2 по блоку"]
        answers = ["Ответ 1", "Ответ 2"]
        return questions, answers

    @staticmethod
    async def generate_test_for_book(idBook: str) -> dict:
        text_blocks_collection = DatabaseFactory.get_text_blocks_collection()
        blocks_cursor = text_blocks_collection.find({"bookId": idBook})
        blocks = [TextBlock.from_document(doc) for doc in blocks_cursor]

        questions = []
        answers = []

        for block in blocks:
            block_questions, block_answers = BackgroundProcessing.generate_questions_for_block(block.original)
            questions.extend(block_questions)
            answers.extend(block_answers)

            text_blocks_collection.update_one(
                {"_id": block._id},
                {
                    "$set": {
                        "questions": block_questions,
                        "rightAnswers": block_answers
                    }
                }
            )

        return {"questions": questions, "answers": answers}

    @staticmethod
    async def get_book_retelling(idBook: str) -> str:
        text_blocks_collection = DatabaseFactory.get_text_blocks_collection()
        blocks_cursor = text_blocks_collection.find({"bookId": idBook})
        summaries = [doc.get("summary") for doc in blocks_cursor if doc.get("summary")]

        return "\n".join(summaries)

    @staticmethod
    async def get_similar_books(idBook: str) -> List[Book]:
        books_collection = DatabaseFactory.get_books_collection()
        random_books_cursor = books_collection.aggregate([{"$sample": {"size": 5}}])        
        return [Book.from_document(doc) for doc in random_books_cursor]