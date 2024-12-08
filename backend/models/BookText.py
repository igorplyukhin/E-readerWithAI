from dataclasses import dataclass
from typing import Optional

@dataclass
class BookText:
    title: str
    authors: str
    content: str
    annotation: Optional[str] = None