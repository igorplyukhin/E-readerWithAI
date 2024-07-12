import BookReader
import Answer_user
import LLaMA
import Divide


def request_second(book_reader, answer_llm, last_res):
    result = LLaMA.llama(book_reader.data + f"Прошлый вопрос и ответа на него: {last_res}", "questions_add", 0)
    result = LLaMA.llama(result, "questions_edit", 0)
    answer_llm.append(result)


def request_first(book_reader, answer_llm):
    result = LLaMA.llama(book_reader.data, "questions", 0)
    result = LLaMA.llama(result, "questions_edit", 0)
    answer_llm.append(result)
    return result

def create_questions(name_file):
    chapters = Divide.split_book_by_chapters(name_file)
    book_reader = BookReader.BookReader(name_file)
    answer = Answer_user.Answer_User(book_reader.data, count_answer=4, block_text=3000)
    number_chapter = 0
    while number_chapter < len(chapters):
        answer_llm = []
        number_chapter = book_reader.reading(chapters, number_chapter)
        print(book_reader.data)
        res_first = request_first(book_reader, answer_llm)
        request_second(book_reader,answer_llm,res_first)
        for count_questions in range(2):
            result = answer_llm[count_questions]
            i = -1
            size = len(result)
            while abs(i) < size and result[i] != '\n':
                i -= 1
            print(result[0:i - 1])
            answer.data = book_reader.data
            if not answer.process_answer(result):
                print("Error")
                return
        book_reader.data = ""


name_file = "book.txt"
create_questions(name_file)
