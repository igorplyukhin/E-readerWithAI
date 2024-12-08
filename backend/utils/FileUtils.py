import os
from typing import List
import PyPDF2
from ebooklib import epub
from bs4 import BeautifulSoup
import tika
from tika import parser

tika.initVM()

class FileUtils:
    @staticmethod
    def save_file(path: str, bytes_data: bytes) -> None:
        """
        Saves a file at the specified path.
        :param path: Path to save the file.
        :param bytes_data: File content as a byte array.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as file:
            file.write(bytes_data)

    @staticmethod
    def check_and_convert_file(file_path: str) -> str:
        """
        Checks the file extension and converts it to a supported format if necessary.
        :param file_path: Path to the file.
        :return: Path to the converted or original file.
        """
        supported_extensions: List[str] = ["txt", "epub", "pdf"]
        file_extension = FileUtils.get_file_extension(file_path).lower()

        if file_extension in supported_extensions:
            if file_extension == "txt":
                return file_path
            elif file_extension == "pdf":
                return FileUtils.convert_pdf_to_txt(file_path)
            elif file_extension == "epub":
                return FileUtils.convert_epub_to_txt(file_path)
            else:
                raise NotImplementedError("Unsupported file format")
        else:
            raise NotImplementedError(f"File format {file_extension} is not supported")

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        Extracts the file extension.
        :param file_path: Path to the file.
        :return: File extension.
        """
        return os.path.splitext(file_path)[1][1:]

    @staticmethod
    def convert_pdf_to_txt(file_path: str) -> str:
        """
        Converts a PDF file to a text file (.txt).
        :param file_path: Path to the PDF file.
        :return: Path to the created text file.
        """
        txt_file_path = os.path.splitext(file_path)[0] + ".txt"

        try:
            with open(file_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

            with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
        except Exception as e:
            raise IOError(f"Error converting PDF to TXT: {str(e)}")

        return txt_file_path

    @staticmethod
    def convert_epub_to_txt(file_path: str) -> str:
        """
        Converts an EPUB file to a text file (.txt) using Apache Tika.
        :param file_path: Path to the EPUB file.
        :return: Path to the created text file.
        """
        txt_file_path = os.path.splitext(file_path)[0] + ".txt"

        try:
            parsed = parser.from_file(file_path)
            text = parsed["content"]

            with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
        except Exception as e:
            raise IOError(f"Error converting EPUB to TXT: {str(e)}")

        return txt_file_path

