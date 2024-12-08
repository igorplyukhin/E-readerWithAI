from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class FictionBook:
    description: Optional['Description'] = None
    body: Optional['Body'] = None

@dataclass
class Description:
    titleInfo: Optional['TitleInfo'] = None
    customInfos: Optional[List['CustomInfo']] = None

@dataclass
class TitleInfo:
    genres: Optional[List[str]] = None
    authors: Optional[List['Author']] = None
    bookTitle: Optional[str] = None
    annotation: Optional['Annotation'] = None
    keywords: Optional[str] = None
    date: Optional[str] = None
    coverPage: Optional['CoverPage'] = None
    lang: Optional[str] = None
    sequence: Optional['Sequence'] = None

@dataclass
class CustomInfo:
    infoType: Optional[str] = None
    value: Optional[str] = None

@dataclass
class Annotation:
    paragraphs: Optional[List[str]] = None

@dataclass
class CoverPage:
    image: Optional['Image'] = None

@dataclass
class Image:
    href: Optional[str] = None

@dataclass
class Sequence:
    name: Optional[str] = None
    number: Optional[str] = None

@dataclass
class Author:
    firstName: Optional[str] = None
    lastName: Optional[str] = None

@dataclass
class Body:
    titles: Optional[List['Title']] = None
    sections: Optional[List['Section']] = None

@dataclass
class Section:
    titles: Optional[List['Title']] = None
    paragraphs: Optional[List[str]] = None
    sections: Optional[List['Section']] = None

@dataclass
class Title:
    paragraphs: Optional[List[str]] = None