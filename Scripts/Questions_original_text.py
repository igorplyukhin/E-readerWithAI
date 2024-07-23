import Divide
def question_orig(book_reader, questions, answer, database):
    chapters = Divide.split_book_by_chapters(questions.file_name)  # разбиваем по главам
    while book_reader.number_chapter < len(chapters):
        if len(chapters[book_reader.number_chapter]) < 200:  # на случай если разбиение произошло неверно
            book_reader.number_chapter += 1
            continue
        book_reader.number_chapter = book_reader.reading(chapters,
                                                         book_reader.number_chapter)  # считываем фрагмент текста
        if book_reader.number_chapter >= len(chapters):
            break
        id_block = database.new_block()
        database.current_block_id = id_block
        database.add_original_text(book_reader.data)
        database.add_id_book()
        print(database.collection_text.find_one({"_id": database.current_block_id})['original'])
        res_first = questions.request_first(book_reader, database)  # Первый вопрос
        questions.request_second(book_reader, res_first, database)  # Второй вопрос
        for number_questions in range(2):
            result = questions.answer_llm[
                questions.count_questions - 2 + number_questions]  # -2 так как массив и обращаемся ко второму вопросу
            answer.data = book_reader.data
            if not answer.process_answer(result, number_questions, database):
                break
        book_reader.data = ""
        next_user = input("Next?(no/enter): ")
        while next_user != "" and next_user != "no" and next_user != 'No':
            next_user = input("Next?(no/enter): ")
        if next_user == "no" or next_user == 'No':
            break
    questions.right_answer = answer.right_answer