from dataclasses import dataclass, field
from typing import List

@dataclass
class User:
    idUser: str
    password: str = ""
    bookIds: List[str] = field(default_factory=list)
    countBook: int = 0