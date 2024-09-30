import os
import ParserFB2
import Divide
import Questions
import BookReader
import Answer_user
import informs_book
import BD


def check_extension(file_path):
    _, file_ext = os.path.splitext(file_path)
    if file_ext.lower() == '.fb2':
        # Обработка файла .fb2 и преобразование в .txt
        new_file_path = ParserFB2.process_fb2(file_path)
        return new_file_path
    elif file_ext.lower() == '.txt':
        return file_path
    else:
        return None


def init_objects(file_path):
    # Убеждаемся, что file_path — это полный путь к файлу
    book_reader = BookReader.BookReader(file_path)
    questions = Questions.Questions(file_path)
    answer_user = Answer_user.User_Answer("", count_answer=4)
    chapters = Divide.split_book_by_chapters(file_path)
    return book_reader, questions, answer_user, chapters


def information(chapters, questions, answer_user, book_reader, name_file):
    title, author = informs_book.title_book(chapters)
    information_book = {
        "about": informs_book.about_book(chapters, title + ' ' + author),
        "retelling": informs_book.retelling(name_file, chapters, questions, answer_user, book_reader,
                                            title + ' ' + author),
        "advice": informs_book.advice_book(chapters, title + ' ' + author),
        "title": title,
        "author": author,
        "name_file": name_file  # Здесь name_file теперь только имя файла
    }
    return information_book


def init_user(login):
    id_user, collection_user = BD.init_user(login)
    database = BD.Database(collection_user, {}, {})
    return database, id_user

