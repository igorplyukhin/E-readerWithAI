import LLaMA
import Summarize
import Divide


def about_book(chapters):

    i = 0
    while len(chapters[i]) < 500:
        i += 1
    name_book = LLaMA.llama(chapters[i], "name", 0, 0, 0)
    if "Нет" in name_book or "нет" in name_book:
        print("Ничего не знаю об этой книге\n")
        return
    print("Wait please...\n")
    result = LLaMA.llama(name_book, "about book", 0, 0, 0)
    result = LLaMA.llama(result, "edit", 0, 0, 0)
    print(result)


def summary(name_file, questions, answer, book_reader):
    name_file_sum = "SummaryBook.txt"
    name_buf_file = "SummarizeAtTime.txt"
    Summarize.summarize(name_file, name_buf_file, False, questions, answer, book_reader)
    for _ in range(2):
        Summarize.summarize(name_buf_file, name_file_sum, False, questions, answer, book_reader)
        buf = name_buf_file
        name_buf_file = name_file_sum
        name_file_sum = buf
    print(open(name_buf_file, "r", encoding="utf-8").read())


def retelling(name_file, chapters, questions, answer, book_reader):
    i = 0
    while len(chapters[i]) < 500:
        i += 1
    name_book = LLaMA.llama(chapters[i], "name", 0, 0, 0)
    if "Нет" in name_book or "нет" in name_book:
        summary(name_file, questions, answer, book_reader)
    else:
        print("Wait please...")
        result = LLaMA.llama(name_book, "retelling", 0, 0, 0)
        result = LLaMA.llama(result, "edit", 0, 0, 0)
        print(result)


def advice_book(chapters):
    i = 0
    while len(chapters[i]) < 500:
        i += 1
    name_book = LLaMA.llama(chapters[i], "name", 0, 0, 0)
    if "Нет" in name_book or "нет" in name_book:
        print("=(")
    else:
        result = LLaMA.llama(name_book, "advice", 0, 0, 0)
        result = LLaMA.llama(result, "edit", 0, 0, 0)
        print(result)
