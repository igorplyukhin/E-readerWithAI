import os
import re
from typing import List

from pdfminer.high_level import extract_text
from bson.objectid import ObjectId

class BookText:
    def __init__(self, title, authors, content, annotation=None):
        self.title = title
        self.authors = authors
        self.content = content
        self.annotation = annotation

class Book:
    def __init__(self, idBook, title, author, description, annotation, status, mode, nameFile, filePath):
        self.idBook = idBook
        self.title = title
        self.author = author
        self.description = description
        self.annotation = annotation
        self.status = status
        self.mode = mode
        self.nameFile = nameFile
        self.filePath = filePath

class TextBlock:
    def __init__(self, _id, original, numberChapter):
        self._id = _id
        self.original = original
        self.numberChapter = numberChapter


class BookProcessor:
    def __init__(self, filePath: str, nameFile: str):
        self.filePath = filePath
        self.nameFile = nameFile

    def readTextFile(self) -> str:
        with open(self.filePath, 'r', encoding='utf-8') as f:
            return f.read()

    def readPdfFile(self) -> str:
        return extract_text(self.filePath)


    def readFb2File(self) -> BookText:  # Requires Fb2Processor implementation (not provided)
        # Placeholder, replace with actual FB2 parsing logic
        raise NotImplementedError("FB2 parsing not implemented")


    def getChapters(self, fileType: str) -> List[str]:
        content = ""
        if fileType == "text/plain":
            content = self.readTextFile()
        elif fileType == "application/pdf":
            content = self.readPdfFile()
        elif fileType == "application/fb2+xml":
            content = self.readFb2File().content
        else:
            raise ValueError("Unsupported file type")
        return [c.strip() for c in re.split(r"(Глава|Часть)\s+\d+", content, flags=re.IGNORECASE) if c.strip()]

    def extractLineContent(self, content: str, prefix: str) -> str:
        match = re.search(rf"(?i){prefix}\s*(.*)", content)
        return match.group(1).strip() if match else None

    def getBook(self, fileType: str) -> Book:
        bookText = None
        if fileType == "text/plain":
            content = self.readTextFile()
            bookText = BookText(
                title=self.extractLineContent(content, "Title:") or "Название не указано",
                authors=self.extractLineContent(content, "Author(s):") or "Автор книги не указан",
                content=self.extractLineContent(content, "Content:") or "Описание отсутствует",
            )
        elif fileType == "application/pdf":
            text = self.readPdfFile()
            bookText = BookText(
                title="Неизвестно",
                authors="Неизвестно",
                content=text,
            )
        elif fileType == "application/fb2+xml":
            bookText = self.readFb2File()
        else:
            raise ValueError("Unsupported file type")

        idBook = str(ObjectId())
        return Book(
            idBook=idBook,
            title=bookText.title,
            author=bookText.authors,
            description=bookText.content,
            annotation=bookText.annotation,
            status="reading",
            mode="default",
            nameFile=self.nameFile,
            filePath=self.filePath,
        )

    def divideChapterIntoBlocks(self, chapter: str) -> List[str]:
        blockSize = 1000
        return [chapter[i:i + blockSize] for i in range(0, len(chapter), blockSize)]

    def processChaptersAndBlocks(self, chapters: List[str]) -> List[TextBlock]:
        textBlocks = []
        for i, chapter in enumerate(chapters):
            blocks = self.divideChapterIntoBlocks(chapter)
            for block in blocks:
                textBlocks.append(TextBlock(
                    _id=str(ObjectId()),
                    original=block,
                    numberChapter=i + 1
                ))
        return textBlocks