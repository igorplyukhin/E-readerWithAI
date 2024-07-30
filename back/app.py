from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Scripts')))
import Scripts.BookReader as BookReader
import Scripts.Questions as Questions
import Scripts.Answer_user as Answer_user
import Scripts.BD as BD
import Scripts.Questions_original_text as Questions_original_text
import Scripts.Summarize as Summarize
import Scripts.initialize as initialize
import Scripts.Divide as Divide

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
book_reader: BookReader.BookReader = BookReader.BookReader("name_file")
questions: Questions.Questions = Questions.Questions("name_file")
answer_user: Answer_user.User_Answer = Answer_user.User_Answer("", 0)
database: BD.Database = BD.Database(None, None, None)
executor = ThreadPoolExecutor(max_workers=3)


# по логину определяем юзера. Возвращаем id всех его книг и описания, названия, авторов и статусы
@app.route('/')
def index():
    return render_template('index.html')




@app.route('/get_user', methods=['POST'])
def get_user():
    global database
    data = request.json
    login = data['login']
    database, id_user = initialize.init_user(login)
    books_id = database.collection_user.find_one({'_id': id_user})['book_id']
    if len(books_id) == 0:
        return jsonify({'count_book': 0,
                        'id_user': id_user,
                        'titles': [],
                        'authors': [],
                        'status': [],
                        'descriptions': []}), 200
    titles, authors, status, descriptions = [], [], [], []
    for id in range(len(books_id)):
        id_book = books_id[id]
        document_book, collection_book = BD.init_book(id_book)
        titles.append(document_book['title'])
        authors.append(document_book['author'])
        status.append(document_book['status'])
        descriptions.append(document_book['description'])
    return jsonify({'count_book': len(books_id), 'id_books': books_id,
                    'id_user': id_user,
                    'titles': titles,
                    'authors': authors,
                    'status': status,
                    'descriptions': descriptions}), 200


@app.route('/upload_book', methods=['POST'])
def upload_book():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    file = request.files['file']
    id_user = request.form.get('id_user')  # Убедитесь, что ID пользователя передан в запросе

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Запускаем фоновую задачу
        # task_id = executor.submit(process_book_in_background, id_user, file_path).result()
        return jsonify(
            {"file_name": file.filename, "status": "success", "message": f"File {file.filename} uploaded successfully",
             "file_path": file_path}), 200


@app.route('/process_book', methods=['POST'])
def process_book_in_background():
    global database, book_reader, questions, answer_user
    data = request.json
    id_user = data['id_user']
    file_path = data['file_path']
    if file_path is None:
        return {"id_book": 0}

    book_reader, questions, answer_user, chapters = initialize.init_objects(file_path)
    information_book = initialize.information(chapters, questions, answer_user, book_reader, file_path)

    document_book, collection_book = BD.init_book(0)
    collection_text = BD.init_text()
    database.collection_text = collection_text
    database.collection_book = collection_book
    id_book = collection_book.count_documents({}) + 1
    document_book, collection_book = BD.create_book(id_book, information_book, id_user)
    database.collection_user.update_one({'_id': id_user},
                                        {"$push": {"book_id": id_book}})
    Divide.split_chapters(chapters, book_reader, database, id_book)
    collection_book.update_one({"_id": id_book}, {"$set": {'status': "reading"}})
    database.collection_user.update_one({"_id": id_user}, {"$inc": {"count_book": 1}})

    # Уведомляем фронтенд через WebSocket
    # socketio.emit('task_complete', {'id_book': id_book}, to=id_user)

    return jsonify({"id_book": id_book})


# def process_book_in_background(id_user, file_path):
#     global database, book_reader, questions, answer_user
#
#     if file_path is None:
#         return {"id_book": 0}
#
#     book_reader, questions, answer_user, chapters = initialize.init_objects(file_path)
#     information_book = initialize.information(chapters, questions, answer_user, book_reader, file_path)
#
#     document_book, collection_book = BD.init_book(0)
#     collection_text = BD.init_text()
#     database.collection_text = collection_text
#     database.collection_book = collection_book
#     id_book = collection_book.count_documents({}) + 1
#     document_book, collection_book = BD.create_book(id_book, information_book, id_user)
#     database.collection_user.update_one({'_id': id_user},
#                                         {"$push": {"book_id": id_book}})
#     Divide.split_chapters(chapters, book_reader, database, id_book)
#     collection_book.update_one({"_id": id_book}, {"$set": {'status': "reading"}})
#     database.collection_user.update_one({"_id": id_user}, {"$inc": {"count_book": 1}})
#
#     # Уведомляем фронтенд через WebSocket
#     socketio.emit('task_complete', {'id_book': id_book}, to=id_user)
#
#     return {"id_book": id_book}


@app.route('/get_book', methods=['POST'])
def get_book():
    global database, book_reader, questions, answer_user
    data = request.json
    id_user = data['id_user']
    id_book = data['id_book']
    if id_book not in database.collection_user.find_one({"_id": id_user})['book_id']:
        return jsonify({'book_id': id_book,
                        'title': "",
                        'author': "",
                        'description': ""
                        }), 400
    document_book, collection_book = BD.init_book(id_book)
    name_file = document_book['name_file']
    book_reader, questions, answer_user, chapters = initialize.init_objects(name_file)
    collection_text = BD.init_text()
    database.collection_text = collection_text
    database.collection_book = collection_book
    return jsonify({'book_id': id_book,
                    'title': document_book['title'],
                    'author': document_book['author'],
                    'description': document_book['description']}), 200


@app.route('/change_mode', methods=['POST'])
def change_mode():
    global book_reader, questions, answer_user, database
    data = request.json
    mode = data['mode']
    id_book = data['id_book']
    id_user = data['id_user']
    text = ''
    if id_book not in database.collection_user.find_one({"_id": id_user})['book_id']:
        return jsonify({"text": ""}), 400
    if mode == 'summarization_time' or mode == 'summarization':
        executor.submit(Summarize.process_chunk, book_reader, 'sum', database, id_book)
        database.collection_book.update_one({"_id": id_book}, {"$set": {"mode": mode}})
        database.collection_book.update_one({"_id": id_book}, {"$set": {"count_ready_block": 3}})
    if mode == 'questions_original_text':
        database.collection_book.update_one({"_id": id_book}, {"$set": {"mode": mode}})
    if mode == 'retelling':
        text = database.collection_book.find_one({"_id": id_book})['retelling']
    if mode == 'test':
        questions_all, right_answers_all = questions.questions_all_book(database, id_book)
        return jsonify({"questions": questions_all,
                        "right_answers": right_answers_all}), 200
    if mode == 'similar_books':
        text = database.collection_book.find_one({"_id": id_book})['advice']

    return jsonify({"text": text}), 200


@app.route('/get_questions', methods=['POST'])
def get_questions():
    global book_reader, questions, answer_user, database
    data = request.json
    id_user = data['id_user']
    id_book = data['id_book']
    id_block = data['id_block']
    if id_book not in database.collection_user.find_one({"_id": id_user})['book_id']:
        return jsonify({"questions": [],
                        "right_answers": []}), 400
    questions, right_answers = Questions_original_text.question_orig(book_reader, questions, answer_user, database,
                                                                     id_block, id_book)
    return jsonify({"questions": questions,
                    "right_answers": right_answers}), 200


@app.route('/get_text', methods=['POST'])
def get_text():
    global book_reader, questions, answer_user, database
    data = request.json
    id_user = data['id_user']
    id_book = data['id_book']
    name_file = database.collection_book.find_one({"_id": id_book})['name_file']

    if id_book not in database.collection_user.find_one({"_id": id_user})['book_id']:
        return jsonify({"text": "",
                        'id_block': 0
                        }), 400
    mode = database.collection_book.find_one({"_id": id_book})['mode']

    text = "error"
    id_block = 0
    if mode == 'summarization_time':
        executor.submit(Summarize.process_chunk, book_reader, 'time', database, id_book)
        text, id_block, reading_time = Summarize.process_text(name_file,
                                                              book_reader, 'time', database, id_book)
        return jsonify({"text": text,
                        "id_block": id_block}), 200
    if mode == 'summarization':
        executor.submit(Summarize.process_chunk, book_reader, 'sum', database, id_book)
        text, id_block, reading_time = Summarize.process_text(name_file,
                                                              book_reader, 'sum', database, id_book)

        return jsonify({"text": text,
                        "id_block": id_block}), 200
    if mode == 'questions_original_text':
        text, id_block = Questions_original_text.get_text(book_reader, questions, answer_user, database, id_book)
    return jsonify({"text": text,
                    "id_block": id_block}), 200


@app.route('/next_block_text', methods=['POST'])
def next_block_text():
    data = request.json
    id_user = data['id_user']
    id_book = data['id_book']
    if id_book not in database.collection_user.find_one({"_id": id_user})['book_id']:
        return jsonify({}), 400
    block_stop = database.collection_book.find_one({"_id": id_book})['block_stop_book']
    count_block = len(database.collection_book.find_one({"_id": id_book})['id_text'])
    if block_stop + 1 < count_block:
        database.collection_book.update_one({"_id": id_book}, {"$inc": {"block_stop_book": 1}})
    return jsonify({}), 200


@app.route('/back_block_text', methods=['POST'])
def back_block_text():
    data = request.json
    id_user = data['id_user']
    id_book = data['id_book']
    if id_book not in database.collection_user.find_one({"_id": id_user})['book_id']:
        return jsonify({}), 400
    block_stop = database.collection_book.find_one({"_id": id_book})['block_stop_book']
    if block_stop > 0:
        database.collection_book.update_one({"_id": id_book}, {"$inc": {"block_stop_book": -1}})
        database.collection_book.update_one({"_id": id_book}, {"$inc": {"count_ready_block": 1}})
    return jsonify({}), 200


# back button
# баг вопросы
# считывание книги сделать
# отладит код
if __name__ == '__main__':
    app.run(debug=True)
