from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpagecontent import PDFPageContent


class PdfProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self) -> str:
        with open(self.file_path, "rb") as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)

            text = ""
            for page in document.get_pages():
                content = PDFPageContent.create_content(page)
                text += content.get_text()
            return text