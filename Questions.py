import BookReader
import Answer_user
import LLaMA
import Divide
class Questions:

#Запрос для второго вопроса
    def __init__(self, file_name):
        self.file_name = file_name
        self.answer_llm = []
        self.count_questions = 0
        self.right_answer = []

    def request_second(self, book_reader, last_res):
        result = LLaMA.llama(book_reader.data + f"Прошлый вопрос и ответы на него: {last_res}", "questions_add", 0, 0, 0)
        result = LLaMA.llama(result, "questions_edit", 0, 0, 0)
        self.answer_llm.append(result)
        self.count_questions += 1

    #Запрос для первого вопроса
    def request_first(self, book_reader):
        result = LLaMA.llama(book_reader.data, "questions", 0, 0, 0)
        result = LLaMA.llama(result, "questions_edit", 0, 0, 0)
        # open_q = LLaMA.llama(book_reader.data, "open questions", 0, 0, 0)
        # open_q = LLaMA.llama(open_q, "edit", 0, 0, 0)
        # print(open_q)
        self.answer_llm.append(result)
        self.count_questions += 1
        return result


    def create_questions(self):
        chapters = Divide.split_book_by_chapters(self.file_name)  # разбиваем по главам
        book_reader = BookReader.BookReader(self.file_name)
        answer = Answer_user.User_Answer(book_reader.data, count_answer=4, block_text=3000)
        while book_reader.number_chapter < len(chapters):
            if len(chapters[book_reader.number_chapter]) < 200:  # на случай если разбиение произошло неверно
                book_reader.number_chapter += 1
                continue
            book_reader.number_chapter = book_reader.reading(chapters, book_reader.number_chapter)  # считываем фрагмент текста
            if book_reader.number_chapter >= len(chapters):
                break
            print(book_reader.data)
            res_first = self.request_first(book_reader)  # Первый вопрос
            self.request_second(book_reader, res_first)  # Второй вопрос
            for number_questions in range(2):
                result = self.answer_llm[self.count_questions - 2 + number_questions]  # -2 так как массив и обращаемся ко второму вопросу
                answer.data = book_reader.data
                if not answer.process_answer(result, number_questions):
                    break
            book_reader.data = ""
        self.right_answer = answer.right_answer

    def questions_all_book(self):
        print("Тест по всей книге\n")
        answer_user = Answer_user.User_Answer("", 0, "")
        for number_question in range(0, len(self.right_answer), 2):  # каждый второй вопрос
            if number_question >= len(self.answer_llm):
                break
            result = self.answer_llm[number_question] # вопрос
            # обрезаем правильный ответ
            i = -1
            size = len(result)
            while abs(i) < size and result[i] != '\n':
                i -= 1
            print(result[0:i - 1])
            answer = answer_user.answerUser()

            if answer == self.right_answer[number_question]:
                print("Правильный ответ =) \n")
            else:
                print("Ответ неверный =( \n")
                print(f"Верный ответ - {self.right_answer[number_question]}")



# file_name = "book.txt"
# questions = Questions(file_name)
# questions.create_questions()
