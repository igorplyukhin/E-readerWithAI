from typing import Optional, List
from pydantic import BaseModel
from bson import ObjectId

class TextBlock(BaseModel):
    _id: str
    original: str
    numberChapter: int = 0
    summary: Optional[str] = None
    summaryTime: Optional[str] = None
    questions: List[str] = []
    rightAnswers: List[str] = []

    def to_document(self) -> dict:
        return {
            "_id": ObjectId(self._id),
            "original": self.original,
            "numberChapter": self.numberChapter,
            "summary": self.summary,
            "summaryTime": self.summaryTime,
            "questions": self.questions,
            "rightAnswers": self.rightAnswers
        }
