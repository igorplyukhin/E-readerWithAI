import Answer_user
import LLaMA


class Questions:

    # Запрос для второго вопроса
    def __init__(self, name_file):
        self.name_file = name_file
        #self.answer_llm = []
        self.count_questions = 0
        #self.right_answer = []

    def request_second(self, book_reader, last_res, database, block_id):
        result = LLaMA.llama(book_reader.data + f"Previous question and answers: {last_res}", "questions_add", 0, 0, 0)
        result = LLaMA.llama(result, "questions_edit", 0, 0, 0)
        #self.answer_llm.append(result)  # бд
        database.add_question(result, block_id)  # парсинг ответов отдельно сделать
        self.count_questions += 1

    # Запрос для первого вопроса
    def request_first(self, book_reader, database, block_id):
        result = LLaMA.llama(book_reader.data, "questions", 0, 0, 0)
        result = LLaMA.llama(result, "questions_edit", 0, 0, 0)
        # open_q = LLaMA.llama(book_reader.data, "open questions", 0, 0, 0)
        # open_q = LLaMA.llama(open_q, "edit", 0, 0, 0)
        # print(open_q)
        #self.answer_llm.append(result) #bd
        database.add_question(result, block_id)  # парсинг ответов отдельно сделать
        self.count_questions += 1
        return result

    def create_questions(self, text, answer, book_reader, database, id_block):
        book_reader.data = text
        answer.data = text  #
        res_first = self.request_first(book_reader, database, id_block)  # Первый вопрос
        self.request_second(book_reader, res_first, database, id_block)  # Второй вопрос
        for number_questions in range(2):
            result = database.collection_text.find_one({"_id": id_block})['questions'][number_questions]
            answer.data = book_reader.data
            if not answer.process_answer(result, number_questions, database, id_block):
                break
        book_reader.data = ""

    def questions_all_book(self, database, id_book):
        answer_user = Answer_user.User_Answer("", 0)
        id_text = database.collection_book.find_one({"_id": id_book})['id_text']
        count_block = len(id_text)
        questions_all = []
        right_answer_all = []
        for number_block in range(count_block):
            if number_block >= count_block:
                break
            #questions = database.collection_text.find_one({"_id": id_text[number_block]})['questions']
            questions = database.collection_text.find_one({"_id": id_text[number_block]}).get('questions', None)

            if questions is None:
                # print("You didnt read book with questions(\n")
                return questions_all, right_answer_all
            right_answers = database.collection_text.find_one({"_id": id_text[number_block]})['right_answers']
            for count_question in range(2):
                question = questions[count_question]
                questions_all.append(question)
                right_answer = right_answers[count_question]
                right_answer_all.append(right_answer)

                # обрезаем правильный ответ
                # i = -1
                # size = len(question)
                # while abs(i) < size and question[i] != '\n':
                #     i -= 1
                # print(question[0:i - 1])
                # answer = answer_user.answerUser()
                # if answer == right_answers[count_question]:
                #     print("Correct answer =) \n")
                # else:
                #     print("Incorrect answer =( \n")
                #     print(f"Correct answer - {right_answers[count_question]}")
        return questions_all, right_answer_all
        #
        # for number_question in range(0, len(self.right_answer), 2):  # каждый второй вопрос
        #     if number_question >= len(self.answer_llm):
        #         break
        #     result = self.answer_llm[number_question]  # вопрос
        #     # обрезаем правильный ответ
        #     i = -1
        #     size = len(result)
        #     while abs(i) < size and result[i] != '\n':
        #         i -= 1
        #     print(result[0:i - 1])
        #     answer = answer_user.answerUser()
        #
        #     if answer == self.right_answer[number_question]:
        #         print("Correct answer =) \n")
        #     else:
        #         print("Incorrect answer =( \n")
        #         print(f"Correct answer - {self.right_answer[number_question]}")
        # print("Test finished\n")
