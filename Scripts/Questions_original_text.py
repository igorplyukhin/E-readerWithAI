import Divide
def question_orig(book_reader, questions, answer):
    chapters = Divide.split_book_by_chapters(questions.file_name)  # разбиваем по главам
    while book_reader.number_chapter < len(chapters):
        if len(chapters[book_reader.number_chapter]) < 200:  # на случай если разбиение произошло неверно
            book_reader.number_chapter += 1
            continue
        book_reader.number_chapter = book_reader.reading(chapters,
                                                         book_reader.number_chapter)  # считываем фрагмент текста
        if book_reader.number_chapter >= len(chapters):
            break
        print(book_reader.data)
        res_first = questions.request_first(book_reader)  # Первый вопрос
        questions.request_second(book_reader, res_first)  # Второй вопрос
        for number_questions in range(2):
            result = questions.answer_llm[
                questions.count_questions - 2 + number_questions]  # -2 так как массив и обращаемся ко второму вопросу
            answer.data = book_reader.data
            if not answer.process_answer(result, number_questions):
                break
        book_reader.data = ""
        next_user = input("Next?(no/enter): ")
        while next_user != "" and next_user != "no" and next_user != 'No':
            next_user = input("Next?(no/enter): ")
        if next_user == "no" or next_user == 'No':
            break
    questions.right_answer = answer.right_answer