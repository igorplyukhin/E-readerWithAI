import LLaMA
import Summarize
import Divide


def title_book(chapters):
    i = 0
    while len(chapters[i]) < 500:
        i += 1
    length = len(chapters[i])
    if length > 5000:
        length = 5000
    name_book = LLaMA.llama(chapters[i][:length], "name", 0, 0, 0)
    name_book = name_book.split(':')
    if name_book[2][0] == " ":
        title = name_book[2][1:]
    else:
        title = name_book[2]
    name_book = name_book[1].split("\n")
    if name_book[0][0] == " ":
        author = name_book[0][1:]
    else:
        author = name_book[0]
    return title, author


def about_book(chapters, name_book):
    if "Нет" in name_book or "нет" in name_book:
        result = "error"
    result = LLaMA.llama(name_book, "about book", 0, 0, 0)
    result = LLaMA.llama(result, "edit", 0, 0, 0)
    return result


def summary(name_file, questions, answer, book_reader):
    name_file_sum = "SummaryBook.txt"
    name_buf_file = "SummarizeAtTime.txt"
    Summarize.summarize(name_file, name_buf_file, False, questions, answer, book_reader)
    for _ in range(2):
        Summarize.summarize(name_buf_file, name_file_sum, False, questions, answer, book_reader)
        buf = name_buf_file
        name_buf_file = name_file_sum
        name_file_sum = buf
    text = open(name_buf_file, "r", encoding="utf-8").read()
    return text


def retelling(name_file, chapters, questions, answer, book_reader, name_book):
    if "Нет" in name_book or "нет" in name_book:
        text = summary(name_file, questions, answer, book_reader)
    else:
        result = LLaMA.llama(name_book, "retelling", 0, 0, 0)
        result = LLaMA.llama(result, "edit", 0, 0, 0)
        text = result
    return text


def advice_book(chapters, name_book):
    if "Нет" in name_book or "нет" in name_book:
        text = "error"
    else:
        result = LLaMA.llama(name_book, "advice", 0, 0, 0)
        result = LLaMA.llama(result, "edit", 0, 0, 0)
        result = LLaMA.llama(result, "translate", 0, 0, 0)
        text = result
    return text
