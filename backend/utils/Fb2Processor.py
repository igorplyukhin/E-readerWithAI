import xml.etree.ElementTree as ET
from dataclasses import dataclass

@dataclass
class BookText:
    title: str
    authors: str
    content: str
    annotation: str

class Fb2Processor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_book_text(self) -> BookText:
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
        except Exception as e:
            raise Exception(f"Error parsing FB2 file: {str(e)}")

        # Extract title
        title = root.find(".//book-title")
        title = title.text if title is not None else "Title not found"

        # Extract authors
        authors = root.findall(".//author")
        author_names = []
        for author in authors:
            first_name = author.find("first-name")
            last_name = author.find("last-name")
            name = f"{first_name.text if first_name is not None else ''} {last_name.text if last_name is not None else ''}".strip()
            if name:
                author_names.append(name)
        authors = ", ".join(author_names) if author_names else "Author not specified"

        # Extract annotation
        annotation = root.find(".//annotation")
        if annotation is not None:
            annotation_text = "\n".join([p.text.strip() for p in annotation.findall("p") if p.text])
        else:
            annotation_text = "Annotation not available"

        # Extract content
        content_builder = []

        # Process titles from <body>
        for title in root.findall(".//body/title"):
            for p in title.findall("p"):
                if p.text:
                    content_builder.append(p.text.strip())

        # Process sections
        for section in root.findall(".//body/section"):
            content_builder.append(self.extract_all_text_from_section(section))

        content = "\n\n".join(content_builder).strip() if content_builder else "Content not available"

        return BookText(title, authors, content, annotation_text)

    def extract_all_text_from_section(self, section: ET.Element) -> str:
        section_content = []

        # Extract titles
        titles = section.findall("title")
        if titles:
            title_text = "\n".join([p.text.strip() for title in titles for p in title.findall("p") if p.text])
            if title_text:
                section_content.append(f"### {title_text} ###")

        # Extract paragraphs
        paragraphs = [p.text.strip() for p in section.findall("p") if p.text]
        if paragraphs:
            section_content.append("\n".join(paragraphs))

        # Process nested sections
        for nested_section in section.findall("section"):
            section_content.append(self.extract_all_text_from_section(nested_section))

        return "\n\n".join(section_content)

