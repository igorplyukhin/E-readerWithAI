import logging
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

class User:
    def __init__(self, idUser, password, bookIds, countBook):
        self.idUser = idUser
        self.password = password
        self.bookIds = bookIds
        self.countBook = countBook

    @classmethod
    def from_document(cls, doc):
        try:
            return cls(
                idUser=doc["_id"],
                password=doc.get("password", ""),
                bookIds=doc.get("bookIds", []),
                countBook=doc.get("countBook", 0),
            )
        except KeyError as e:
            raise ValueError(f"Missing required field in User document: {e}")


    def to_document(self):
        return {
            "_id": self.idUser,
            "password": self.password,
            "bookIds": self.bookIds,
            "countBook": self.countBook,
        }


class Book:
    def __init__(self, idBook, title, author, description, annotation, status, mode, nameFile, filePath, blockStopBook, chapterStopBook, textBlockIds):
        self.idBook = idBook
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

    @classmethod
    def from_document(cls, doc):
        logger.info(f"Mapping Document to Book: annotation={doc.get('annotation')}, textBlockIds.size={len(doc.get('textBlockIds', []))}")
        logger.info(f"First 5 textBlockIds: {doc.get('textBlockIds', [])[:5]}")

        try:
            return cls(
                idBook=str(doc["_id"]),
                title=doc["title"],
                author=doc["author"],
                description=doc["description"],
                annotation=doc.get("annotation"),
                status=doc.get("status", "reading"),
                mode=doc.get("mode", "default"),
                nameFile=doc["nameFile"],
                filePath=doc["filePath"],
                blockStopBook=doc.get("blockStopBook", 0),
                chapterStopBook=doc.get("chapterStopBook", 0),
                textBlockIds=doc.get("textBlockIds", []),
            )
        except KeyError as e:
            raise ValueError(f"Missing required field in Book document: {e}")

    def to_document(self):
        doc = {
            "_id": ObjectId(self.idBook),
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
            "textBlockIds": self.textBlockIds,
        }
        return doc

class TextBlock:
    def __init__(self, _id, original, numberChapter, summary=None, summaryTime=None, questions=None, rightAnswers=None):
        self._id = _id
        self.original = original
        self.numberChapter = numberChapter
        self.summary = summary
        self.summaryTime = summaryTime
        self.questions = questions or []
        self.rightAnswers = rightAnswers or []

    @classmethod
    def from_document(cls, doc):
        try:
            return cls(
                _id=str(doc["_id"]),
                original=doc["original"],
                numberChapter=doc["numberChapter"],
                summary=doc.get("summary"),
                summaryTime=doc.get("summaryTime"),
                questions=doc.get("questions", []),
                rightAnswers=doc.get("rightAnswers", []),
            )
        except KeyError as e:
            raise ValueError(f"Missing required field in TextBlock document: {e}")

    def to_document(self):
        return {
            "_id": ObjectId(self._id),
            "original": self.original,
            "numberChapter": self.numberChapter,
            "summary": self.summary,
            "summaryTime": self.summaryTime,
            "questions": self.questions,
            "rightAnswers": self.rightAnswers,
        }