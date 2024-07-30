import LLaMA  # Импорт модуля LLaMA для работы с внешним API
import proccesing_answer_LLM as a_llm  # Импорт модуля proccesing_answer_LLM для обработки ответов

class User_Answer:
    def __init__(self, data, count_answer):
        """
        Конструктор класса Answer_User.

        Параметры:
        - data: данные для обработки (предположительно текст или запрос)
        - count_answer: количество вариантов ответов (integer)
        - block_text: блокировка текста (integer), возможно, связанная с каким-то условием
        """
        self.right_answer = []
        self.data = data  # Инициализация данных для обработки
        self.count_answer = count_answer  # Инициализация количества вариантов ответов
    def answerUser(self):
        """
        Метод для получения ответа пользователя.

        Возвращает:
        - Ответ пользователя в виде строки (str)
        """
        answer_user = input("Your answer: ")  # Получение ответа пользователя через консольный ввод
        while not answer_user.isdigit() or int(answer_user) > 4 or int(answer_user) < 1:
            if answer_user.isdigit() == 1:
                print(f"Choose answer options 1 - {self.count_answer}!")
            else:
                print("Enter a number!")
            answer_user = input("Your answer: ")
        return answer_user

    def search_right_answer(self, result, number_question, database, id_block):
        """
        Метод для поиска правильного ответа.

        Параметры:
        - result: результат обработки или запроса (предположительно строка или список)

        Возвращает:
        - Правильный ответ в виде строки (str), либо 0, если не удалось найти правильный ответ
        """
        i = -1
        while result[i].isdigit() == 0 or (int(result[i]) not in range(1, self.count_answer + 1)):
            if i < -50:
                return 0
            i -= 1
        if a_llm.right_answer(result[i], result):
            return 0
        right_answer = result[i]
        count_call = 0
        while right_answer == 0:
            if number_question == 0:
                result = LLaMA.llama(self.data, "questions", 0, 0, 0)  # Выполнение запроса к внешнему API
            else:
                result = LLaMA.llama(self.data, "questions_add", 0, 0, 0)  # Выполнение запроса к внешнему API
            right_answer = self.search_right_answer(result, number_question, database, id_block)  # Повторный поиск правильного ответа
            count_call += 1
            if count_call == 3:
                break
        if count_call != 0:
            database.collection_text.update_one({"_id": id_block},
                                                {"$set": {f"questions.{number_question}": result}})
        return right_answer

    def process_answer(self, result, number_question, database, id_block, answer_user, id_book):
        text_min = 2000
        text_max = 5000
        """
        Метод для обработки ответа пользователя и проверки его правильности.

        Параметры:
        - result: результат обработки или запроса (предположительно строка или список)

        Возвращает:
        - True, если ответ правильный, False в противном случае
        """
        right_answer = self.search_right_answer(result)  # Поиск правильного ответа
        count_call = 0
        while right_answer == 0:
            if number_question == 0:
                result = LLaMA.llama(self.data, "questions", 0, 0, 0)  # Выполнение запроса к внешнему API
            else:
                result = LLaMA.llama(self.data, "questions_add", 0, 0, 0)  # Выполнение запроса к внешнему API
            right_answer = self.search_right_answer(result)  # Повторный поиск правильного ответа
            count_call += 1
            if count_call == 3:
                break
        if right_answer == 0:
            return False
        if count_call != 0:
            database.collection_text.update_one({"_id": id_block},
                                                {"$set": {f"questions.{number_question}": result}})
        #database.add_right_answer(right_answer, id_block)
        # Обрезаем правильный ответ для пользователя
        i = -1
        size = len(result)
        while abs(i) < size and result[i] != '\n':
            i -= 1
        print(result[0:i - 1])  # Вывод обработанного результата
        answer_user = self.answerUser()  # Получение ответа пользователя
        block_text = database.collection_book.find_one({"_id": id_book})['block_text']
        if answer_user == right_answer:
            if block_text < text_max:
                block_text += 100  # Изменение части текста который считываем
            print("Correct answer =)")
        else:
            if block_text > text_min:
                block_text -= 200  # Изменение части текста который считываем
            print("Incorrect answer =(\n")
            print(f"Correct answer - {right_answer}")  # Вывод правильного ответа в случае ошибки пользователя
        database.collection_book.update_one({"_id": id_book},
                                            {"$set": {"block_text": block_text}})
        return True
