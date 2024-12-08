import uuid
from bson import ObjectId, DBRef
import json


class Book:
    def __init__(self, title, author, description, nameFile, filePath, annotation=None, status="reading", mode="default", blockStopBook=0, chapterStopBook=0, textBlockIds=[]):
        self.idBook = str(uuid.uuid4()) # Используем UUID вместо ObjectId для простоты,  ObjectId  можно использовать с pymongo
        self.title = title
        self.author = author
        self.description = description
        self.annotation = annotation
        self.status = status
        self.mode = mode
        self.nameFile = nameFile
        self.filePath = filePath
        self.blockStopBook = blockStopBook
        self.chapterStopBook = chapterStopBook
        self.textBlockIds = textBlockIds

    def to_document(self):
        #  Можно использовать  ObjectId из pymongo  если у вас есть подключение к базе.
        #   doc = {"_id": ObjectId(self.idBook), ...} 
        doc = {
            "_id": self.idBook,
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "annotation": self.annotation,
            "status": self.status,
            "mode": self.mode,
            "nameFile": self.nameFile,
            "filePath": self.filePath,
            "blockStopBook": self.blockStopBook,
            "chapterStopBook": self.chapterStopBook,
            "textBlockIds": self.textBlockIds,  # Здесь сохраняем как list строк
        }
        return doc

    def to_json(self):
        return json.dumps(self.to_document(), default=str) # default=str обрабатывает ObjectId

#Пример использования
book = Book(
    title="The Hitchhiker's Guide to the Galaxy",
    author="Douglas Adams",
    description="A humorous science fiction comedy.",
    nameFile="hitchhikers_guide.txt",
    filePath="/path/to/file.txt",
    textBlockIds=["12345", "67890"]
)

print(book.to_json())

#  Для работы с MongoDB:
# import pymongo
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["your_database_name"]
# collection = db["books"]
# collection.insert_one(book.to_document())