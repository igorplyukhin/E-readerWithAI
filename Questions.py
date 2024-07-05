import BookReader
import Answer_user
import LLaMA
def create_questions(name_file):
    book_reader = BookReader.BookReader(name_file)
    answer = Answer_user.Answer_User(book_reader.data, count_answer=4, block_text=3000)
    with open(book_reader.name_file, 'r', encoding='utf-8') as book:
        while book_reader.end_file:
            book_reader.read_block(book)
            if book_reader.count_symbols == book_reader.block_text:
                book_reader.read_until_paragraph(book)
            print(book_reader.data)
            result = LLaMA.llama(book_reader.data, "questions", 0)
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
