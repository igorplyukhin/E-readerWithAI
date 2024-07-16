import Questions
import Answer_user
import BookReader
text = ""
def question_sum(text, book_reader, questions):
    answer = Answer_user.User_Answer(text, count_answer=4, block_text=3000)
    book_reader = BookReader.BookReader(self.file_name)
    answer = Answer_user.User_Answer(book_reader.data, count_answer=4, block_text=3000)
    print(text)
    res_first = questions.request_first(book_reader)  # Первый вопрос
    questions.request_second(book_reader, res_first)  # Второй вопрос
    for number_questions in range(2):
        result = questions.answer_llm[
            questions.count_questions - 2 + number_questions]  # -2 так как массив и обращаемся ко второму вопросу
        answer.data = book_reader.data
        if not answer.process_answer(result, number_questions):
            break
