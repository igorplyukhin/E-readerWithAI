import os
import ParserFB2
import Divide
import Questions
import BookReader
import Answer_user
import informs_book
import BD


def check_extension(name_file):
    file_name, file_exp = os.path.splitext(name_file)
    if file_exp == ".fb2":
        file_name = ParserFB2.process_fb2(file_name, f'uploads/{name_file}')
        print(file_name, file_exp)
        return file_name
    if file_exp == ".txt":
        return name_file
    return None


def init_objects(name_file):
    chapters = Divide.split_book_by_chapters(name_file)
    book_reader = BookReader.BookReader(name_file)
    questions = Questions.Questions(name_file)
    answer_user = Answer_user.User_Answer("", count_answer=4)

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
        "name_file": name_file
    }
    return information_book


def init_user(login):
    id_user, collection_user = BD.init_user(login)
    database = BD.Database(collection_user, {}, {})
    return database, id_user

