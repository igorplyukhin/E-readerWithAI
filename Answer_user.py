import LLaMA

class Answer_User:
    def __init__(self,data, count_answer, block_text):
        self.data = data
        self.count_answer = count_answer
        self.block_text = block_text
    def answerUser(self):
        answer_user = input("Ваш ответ: ")
        while not answer_user.isdigit() or int(answer_user) > 4 or int(answer_user) < 1:
            if answer_user.isdigit() == 1:
                print(f"Выберете варианты ответа 1 - {self.count_answer}!")
            else:
                print("Введите число!")
            answer_user = input("Ваш ответ: ")
        return answer_user
    def search_right_answer(self, result):
        i = -1
        while result[i].isdigit() == 0 or (int(result[i]) not in range(1, self.count_answer+1)):
            if i < -50:
                return 0
            i -= 1
        return result[i]
    def process_answer(self, result):
        right_answer = self.search_right_answer(result)
        count_call = 0
        while right_answer == 0:
            result = LLaMA.llama(self.data, "questions", 0)
            right_answer = self.search_right_answer(result)
            count_call += 1
            if count_call == 3:
                break
        if right_answer == 0:
            print("Error")
            return False
        answer_user = self.answerUser()
        if answer_user == right_answer:
            if self.block_text < 3000:
                self.block_text += 100
            print("Ответ правильный =)")
        else:
            if self.block_text > 2000:
                self.block_text -= 200
            print("Ответ неправильный =(")
        return True

