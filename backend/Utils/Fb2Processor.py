import xml.etree.ElementTree as ET
from models.BookText import BookText

class Fb2Processor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ns = {'fb2': 'http://www.gribuser.ru/xml/fictionbook/2.0'}

    def extract_book_text(self) -> BookText:
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        title_info = root.find('fb2:description/fb2:title-info', self.ns)
        title = "Название не найдено"
        authors_str = "Автор не указан"
        annotation = "Аннотация отсутствует"

        if title_info is not None:
            t = title_info.find('fb2:book-title', self.ns)
            if t is not None and t.text:
                title = t.text.strip()

            authors = title_info.findall('fb2:author', self.ns)
            if authors:
                authors_list = []
                for a in authors:
                    first_name = a.find('fb2:first-name', self.ns)
                    last_name = a.find('fb2:last-name', self.ns)
                    fn = first_name.text.strip() if first_name is not None and first_name.text else ""
                    ln = last_name.text.strip() if last_name is not None and last_name.text else ""
                    full_name = f"{fn} {ln}".strip()
                    if full_name:
                        authors_list.append(full_name)
                if authors_list:
                    authors_str = ", ".join(authors_list)

            ann = title_info.find('fb2:annotation', self.ns)
            if ann is not None:
                ann_paragraphs = []
                for p in ann.findall('fb2:p', self.ns):
                    if p.text:
                        ann_paragraphs.append(p.text.strip())
                if ann_paragraphs:
                    annotation = "\n".join(ann_paragraphs)

        content_builder = []
        body = root.find('fb2:body', self.ns)
        if body is not None:
            for title_elem in body.findall('fb2:title', self.ns):
                for p in title_elem.findall('fb2:p', self.ns):
                    if p.text:
                        content_builder.append(p.text.strip())
                content_builder.append("")

            for section in body.findall('fb2:section', self.ns):
                section_text = self.extractAllTextFromSection(section)
                if section_text.strip():
                    content_builder.append(section_text.strip())
                    content_builder.append("")

        content_str = "\n\n".join([c for c in content_builder if c.strip()])
        if not content_str:
            content_str = "Содержание отсутствует"

        return BookText(
            title=title,
            authors=authors_str,
            content=content_str,
            annotation=annotation
        )

    def extractAllTextFromSection(self, section):
        texts = []
        # Используем неймспейс
        titles = section.findall('fb2:title', self.ns)
        for title_elem in titles:
            title_pars = [p.text.strip() for p in title_elem.findall('fb2:p', self.ns) if p.text and p.text.strip()]
            if title_pars:
                texts.append("### " + " ".join(title_pars) + " ###")

        pars = [p.text.strip() for p in section.findall('fb2:p', self.ns) if p.text and p.text.strip()]
        if pars:
            texts.append("\n".join(pars))

        nested_sections = section.findall('fb2:section', self.ns)
        for nested_section in nested_sections:
            nested_text = self.extractAllTextFromSection(nested_section)
            if nested_text.strip():
                texts.append(nested_text.strip())

        return "\n\n".join(texts)
