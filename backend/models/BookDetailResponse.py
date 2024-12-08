from dataclasses import dataclass
from typing import List

@dataclass
class BookDetailResponse:
    annotation: str
    totalPages: int
    textBlocks: List[str]