from flask import Flask, request, jsonify
from Scripts import Divide, BookReader, Questions, Answer_user, informs_book, ParserFB2, BD
import os

app = Flask(__name__)
book_reader: BookReader.BookReader = BookReader.BookReader("name_file")
questions: Questions.Questions = Questions.Questions("name_file")
answer_user: Answer_user.User_Answer = Answer_user.User_Answer("", 0)
database: BD.Database = BD.Database(None, None, None, 0, 0)

def check_extension(name_file):
    file_name, file_exp = os.path.splitext(f"C:/Users/miros/PycharmProjects/BookAI/Scripts/{name_file}")  # Убрать
    if file_exp == ".fb2":
        file_name = ParserFB2.process_fb2(name_file)
        return file_name
    if file_exp == ".txt":
        return name_file
    return None


def init_objects(name_file):
    name_file = check_extension(name_file)
    if name_file is None:
        print("Other format book\n")
    chapters = Divide.split_book_by_chapters(name_file)
    book_reader = BookReader.BookReader()
    questions = Questions.Questions()
    book_reader.name_file = name_file
    questions.name_file = name_file
    answer_user = Answer_user.User_Answer("", count_answer=4)

    return book_reader, questions, answer_user, chapters


def information(chapters, questions, answer_user, book_reader):
    title, author = informs_book.title_book(chapters)
    information_book = {
        "about": informs_book.about_book(chapters, title + ' ' + author),
        "retelling": informs_book.retelling(book_reader.name_file, chapters, questions, answer_user, book_reader,
                                            title + ' ' + author),
        "advice": informs_book.advice_book(chapters, title + ' ' + author),
        "title": title,
        "author": author
    }
    return information_book


def init_user(login):
    document_user, collection_user = BD.init_user(login)
    database = BD.Database(collection_user, {}, {}, document_user['_id'], 0)
    return database


# по логину определяем юзера. Возвращаем id всех его книг и описания, названия, авторов и статусы
@app.route('/initialize_user', methods=['POST'])
def initialize_user():
    global database
    data = request.json
    login = data['login']
    database = init_user(login)
    books_id = database.collection_user.find_one({'_id': database.id_user})['book_id']
    if len(books_id) == 0:
        return jsonify({'count_book': 0})
    titles, authors, status, descriptions = [], [], [], []
    for id in range(len(books_id)):
        id_book = books_id[id]
        document_book, collection_book = BD.init_book(id_book)
        titles.append(document_book['title'])
        authors.append(document_book['author'])
        status.append(document_book['status'])
        descriptions.append(document_book['description'])
    return jsonify({'count_book': len(books_id),'id_books': books_id,
                    'id_user': database.id_user,
                    'titles': titles,
                    'authors': authors,
                    'status': status,
                    'descriptions': descriptions})


# получаем id книги и возвращаем данные для отображения ее начальной страницы
@app.route('/initialize_book', methods=['POST'])
def initialize_book():
    global database, book_reader, questions, answer_user
    data = request.json
    id_book = data['id_book']
    document_book, collection_book = BD.init_book(id_book)
    if document_book is None:
        name_file = data['name_file']
        book_reader, questions, answer_user, chapters = init_objects(name_file)
        information_book = information(chapters, questions, answer_user, book_reader)
        document_book, collection_book = BD.create_book(id_book, information_book, database.id_user)
        database.collection_user.update_one({'_id': database.id_user},
                                            {"$push": {"book_id": id_book}})
    else:
        name_file = document_book['name_file']
        book_reader, questions, answer_user, chapters = init_objects(name_file)
    collection_text = BD.init_text()
    database.id_book = id_book
    database.collection_text = collection_text
    database.collection_book = collection_book
    return jsonify({'book_id': id_book, 'title': document_book['title'],
                    'author': document_book['author'],
                    'description': document_book['description']})


# @app.route('/initialize', methods=['POST'])
# def initialize():
#     global book_reader, questions, answer_user, database
#     data = request.json
#     name_file = data['file_name']
#     login = data['login']
#     book_reader, questions, answer_user, chapters = init_objects(name_file)
#     database = init_documents(login, chapters, questions, answer_user, book_reader)
#
#     chapters = Divide.split_book_by_chapters(name_file)
#     if database.collection_book.find_one({"_id": database.id_book})['status'] == 'start':
#
#         Divide.split_chapters(chapters, book_reader, database)
#         database.collection_book.update_one({"_id": database.id_book}, {"$set": {'status': "reading"}})
#     return jsonify({'status': 'initialized', 'file_name': name_file})


# @app.route('/get_next_chunk', methods=['GET'])
# def get_next_chunk():
#     global book_reader, database
#
#     if not book_reader or not database:
#         return jsonify({'status': 'error', 'message': 'Not initialized'}), 400
#     print (database.collection_book.find_one({"_id": database.id_book}))
#     book_reader.number_chapter = database.collection_book.find_one({"_id": database.id_book})['chapter_stop_book']
#     book_reader.count_block = database.collection_book.find_one({"_id": database.id_book})['block_stop_book']
#     id_text = database.collection_book.find_one({"_id": database.id_book})['id_text']
#
#     if book_reader.count_block < len(id_text):
#         id_block = id_text[book_reader.count_block]
#         text = database.collection_text.find_one({"_id": id_block})['original']
#         book_reader.data = text
#         database.current_block_id = id_block
#         res_first = questions.request_first(book_reader, database)  # Первый вопрос
#         questions.request_second(book_reader, res_first, database)  # Второй вопрос
#         return jsonify({'text': text, 'block_id': id_block})
#     else:
#         return jsonify({'status': 'no more blocks'})
#

# @app.route('/get_questions', methods=['GET'])
# def get_questions():
#     global book_reader, database
#
#     if not book_reader or not database:
#         return jsonify({'status': 'error', 'message': 'Not initialized'}), 400
#     data = request.json
#     id_text = data['block_id']
#     questions_arr = database.collection_text.find_one({"_id": id_text})
#
#     return jsonify({'questions': questions_arr})
#
#
# @app.route('/answer_question', methods=['POST'])
# def answer_question():
#     global book_reader, answer_user, database
#     if not book_reader or not answer_user or not database:
#         return jsonify({'status': 'error', 'message': 'Not initialized'}), 400
#
#     data = request.json
#     block_id = data['block_id']
#     user_answer = data['answer']
#     number_questions = data['question_number']
#
#     book_reader.data = database.collection_text.find_one({"_id": block_id})['original']
#     answer_user.data = book_reader.data
#
#     result = database.collection_text.find_one({"_id": block_id})['questions'][number_questions]
#     correct: bool = answer_user.process_answer(result, number_questions, database, block_id, user_answer)
#
#     return jsonify({'correct': correct})
#
#
# @app.route('/next', methods=['POST'])
# def next():
#     global book_reader, database
#     if not book_reader or not database:
#         return jsonify({'status': 'error', 'message': 'Not initialized'}), 400
#
#     data = request.json
#     next_user = data.get('next_user', '').lower()
#
#     if next_user in ["no", ""]:
#         chapter = {"chapter_stop_book": book_reader.number_chapter}
#         database.collection_book.update_one({"_id": database.id_book}, {"$set": chapter})
#         return jsonify({'status': 'stopped', 'chapter_stop_book': book_reader.number_chapter})
#
#     book_reader.count_block += 1
#     return jsonify({'status': 'next block', 'block_number': book_reader.count_block})


if __name__ == '__main__':
    app.run(debug=True)
