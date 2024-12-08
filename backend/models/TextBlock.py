from dataclasses import dataclass, field
from typing import List, Optional
from bson import ObjectId

@dataclass
class TextBlock:
    _id: str
    original: str
    numberChapter: int = 0
    summary: Optional[str] = None
    summaryTime: Optional[str] = None
    questions: List[str] = field(default_factory=list)
    rightAnswers: List[str] = field(default_factory=list)

    def to_document(self):
        return {
            "_id": ObjectId(self._id),
            "original": self.original,
            "numberChapter": self.numberChapter,
            "summary": self.summary,
            "summaryTime": self.summaryTime,
            "questions": self.questions,
            "rightAnswers": self.rightAnswers
        }