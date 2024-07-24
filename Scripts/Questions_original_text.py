import Divide
def question_orig(book_reader, questions, answer, database):
    if database.collection_book.find_one({'_id': database.id_book})['status'] == 'start':
        chapters = Divide.split_book_by_chapters(questions.file_name)  # Разделение книги на главы
        Divide.split_chapters(chapters, book_reader, database)
        database.collection_book.update_one({"_id": database.id_book}, {"$set": {'status': "reading"}})
    book_reader.number_chapter = database.collection_book.find_one({"_id": database.id_book})['chapter_stop_book']
    book_reader.count_block = database.collection_book.find_one({"_id": database.id_book})['block_stop_book']
    while book_reader.count_block < len(database.collection_book.find_one({'_id': database.id_book})['id_text']):
        # book_reader.number_chapter = book_reader.reading(chapters,
        #                                                  book_reader.number_chapter)  # считываем фрагмент текста
        id_text = database.collection_book.find_one({"_id": database.id_book})['id_text']
        id_block = id_text[book_reader.count_block]
        text = database.collection_text.find_one({"_id": id_block})['original']
        print(text)
        book_reader.data = text
        database.current_block_id = id_block
        res_first = questions.request_first(book_reader, database)  # Первый вопрос
        questions.request_second(book_reader, res_first, database)  # Второй вопрос
        for number_questions in range(2):
            result = database.collection_text.find_one({"_id": database.current_block_id})['questions'][number_questions]
            answer.data = book_reader.data
            if not answer.process_answer(result, number_questions, database, id_block):
                break
        book_reader.data = ""
        next_user = input("Next?(no/enter): ")
        while next_user != "" and next_user != "no" and next_user != 'No':
            next_user = input("Next?(no/enter): ")
        if next_user == "no" or next_user == 'No':
            chapter = {"chapter_stop_book": book_reader.number_chapter}
            database.collection_book.update_one({"_id": database.id_book}, {"$set": chapter})  #Запомнили где остановились в чтении
            break
        book_reader.count_block += 1
    database.add_block_stop(book_reader.count_block)  # запомним фрагмент на котором остановился читатель
    database.add_chapter_stop(book_reader.number_chapter)
    #questions.right_answer = answer.right_answer