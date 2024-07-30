import Divide


def get_text(book_reader, questions, answer_user, database, id_book):
    if database.collection_book.find_one({'_id': id_book})['status'] == 'start':
        file_path = f"uploads/{book_reader.name_file}"
        chapters = Divide.split_book_by_chapters(file_path)  # Разделение книги на главы
        Divide.split_chapters(chapters, book_reader, database, id_book)
        database.collection_book.update_one({"_id": id_book}, {"$set": {'status': "reading"}})
    book_reader.number_chapter = database.collection_book.find_one({"_id": id_book})['chapter_stop_book']
    book_reader.count_block = database.collection_book.find_one({"_id": id_book})['block_stop_book']
    if book_reader.count_block < len(database.collection_book.find_one({'_id': id_book})['id_text']):
        id_text = database.collection_book.find_one({"_id": id_book})['id_text']
        id_block = id_text[book_reader.count_block]
        text = database.collection_text.find_one({"_id": id_block})['original']
        database.add_block_stop(book_reader.count_block, id_book)  # запомним фрагмент на котором остановился читатель
        database.add_chapter_stop(book_reader.number_chapter, id_book)
        return text, id_block
    return "end_file", 0


def correct_questions(result):
    # Обрезаем правильный ответ для пользователя
    i = -1
    size = len(result)
    while abs(i) < size and result[i] != '\n':
        i -= 1
    return result[0:i - 1]

def question_orig(book_reader, questions, answer_user, database, id_block, id_book):
    book_reader.number_chapter = database.collection_book.find_one({"_id": id_book})['chapter_stop_book']
    # book_reader.count_block = database.collection_book.find_one({"_id": database.id_book})['block_stop_book']
    if book_reader.count_block < len(database.collection_book.find_one({'_id':  id_book})['id_text']):
        # text = give_text(book_reader, questions, answer, database)
        # print(text)
        mode = database.collection_book.find_one({"_id":  id_book})['mode']
        text = database.collection_text.find_one({'_id': id_block})['original']
        # if mode == 'summarization_time':
        #     text = database.collection_text.find_one({'_id': id_block})['sum_time']
        # if mode == 'summarization':
        #     text = database.collection_text.find_one({'_id': id_block})['sum']

        book_reader.data = text
        # id_text = database.collection_book.find_one({"_id": database.id_book})['id_text']
        database.current_block_id = id_block
        res_first = questions.request_first(book_reader, database, id_block)  # Первый вопрос
        questions.request_second(book_reader, res_first, database, id_block)  # Второй вопрос
        result = database.collection_text.find_one({"_id": id_block})['questions']
        database.collection_text.update_one({"_id": id_block},
                                            {"$set": {"questions": []}})
        database.collection_text.update_one({"_id": id_block},
                                            {"$set": {"right_answers": []}})
        for number_question in range(2):
            right_answer = answer_user.search_right_answer(result[number_question], number_question, database, id_block)
            database.add_right_answer(right_answer, id_block)
            question = correct_questions(result[number_question])
            database.collection_text.update_one({"_id": id_block},
                                                {"$push": {"questions": question}})
        book_reader.data = ""
        right_answer = database.collection_text.find_one({"_id": id_block})['right_answers']
        result = database.collection_text.find_one({"_id": id_block})['questions']
        return result, right_answer


        # next_user = input("Next?(no/enter): ")
        # while next_user != "" and next_user != "no" and next_user != 'No':
        #     next_user = input("Next?(no/enter): ")
        # if next_user == "no" or next_user == 'No':
        #     chapter = {"chapter_stop_book": book_reader.number_chapter}
        #     database.collection_book.update_one({"_id": database.id_book}, {"$set": chapter})  #Запомнили где остановились в чтении
    return [], []
    #questions.right_answer = answer.right_answer