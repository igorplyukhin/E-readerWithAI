from flask import Flask, request, jsonify, render_template
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
from werkzeug.utils import secure_filename
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

    # Инициализация пользователя и получение данных из базы
    database, id_user = initialize.init_user(login)
    user_data = database.collection_user.find_one({'_id': id_user})
    
    if not user_data:
        return jsonify({'count_book': 0,
                        'id_user': id_user,
                        'titles': [],
                        'authors': [],
                        'status': [],
                        'descriptions': []}), 200
    
    books_id = user_data.get('book_id', [])
    if len(books_id) == 0:
        return jsonify({'count_book': 0,
                        'id_user': id_user,
                        'titles': [],
                        'authors': [],
                        'status': [],
                        'descriptions': []}), 200
    
    # Подготовка списков с данными о книгах
    titles, authors, status, descriptions = [], [], [], []
    for id in books_id:
        document_book, collection_book = BD.init_book(id)
        if document_book:
            titles.append(document_book.get('title', ''))
            authors.append(document_book.get('author', ''))
            status.append(document_book.get('status', ''))
            descriptions.append(document_book.get('description', ''))
    
    return jsonify({'count_book': len(books_id),
                    'id_books': books_id,
                    'id_user': id_user,
                    'titles': titles,
                    'authors': authors,
                    'status': status,
                    'descriptions': descriptions}), 200


@app.route('/upload_book', methods=['POST'])
def upload_book():
    try:
        # Проверяем, пришел ли файл в запросе
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400

        file = request.files['file']
        id_user = request.form.get('id_user')

        # Проверка на наличие ID пользователя
        if not id_user:
            return jsonify({'status': 'error', 'message': 'User ID is missing'}), 400

        # Проверка на то, что файл выбран
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'}), 400

        if file:
            # Безопасно сохраняем имя файла
            filename = secure_filename(file.filename)
            # Формируем полный путь к файлу
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Сохраняем файл
            file.save(file_path)
            app.logger.info(f"File saved to {file_path}")

            # Проверяем, что файл действительно был сохранён
            if not os.path.exists(file_path):
                app.logger.error(f"File {file_path} was not saved correctly.")
                return jsonify({'status': 'error', 'message': 'File was not saved correctly'}), 500

            # Проверяем расширение файла, передавая полный путь
            new_file_path = initialize.check_extension(file_path)
            if not new_file_path:
                return jsonify({'status': 'error', 'message': 'Unsupported file type'}), 400

            # Если файл был преобразован (например, из .fb2 в .txt), обновляем путь
            if new_file_path != file_path:
                app.logger.info(f"File converted to {new_file_path}")
                file_path = new_file_path

            # Запускаем обработку книги в фоне
            executor.submit(process_book_in_background, id_user, file_path)

            # Логируем информацию об успешной загрузке
            app.logger.info(f"File {filename} uploaded by user {id_user}")

            # Возвращаем ответ
            return jsonify({
                "file_name": filename,
                "status": "success",
                "message": f"File {filename} uploaded successfully and is being processed",
                "file_path": file_path
            }), 200

    except Exception as e:
        app.logger.error(f"Error during file upload: {str(e)}")
        return jsonify({'status': 'error', 'message': f"An error occurred during file upload: {str(e)}"}), 500



def process_book_in_background(id_user, file_path):
    global database, book_reader, questions, answer_user

    if file_path is None:
        return {"id_book": 0}

    # Используем полный путь к файлу для чтения
    book_reader, questions, answer_user, chapters = initialize.init_objects(file_path)
    # Получаем только имя файла
    file_name = os.path.basename(file_path)
    # Сохраняем информацию о книге с именем файла
    information_book = initialize.information(chapters, questions, answer_user, book_reader, file_name)

    document_book, collection_book = BD.init_book(0)
    collection_text = BD.init_text()
    database.collection_text = collection_text
    database.collection_book = collection_book
    id_book = collection_book.count_documents({}) + 1
    document_book, collection_book = BD.create_book(id_book, information_book, id_user)
    database.collection_user.update_one({'_id': int(id_user)},
                                        {"$push": {"book_id": id_book}})
    Divide.split_chapters(chapters, book_reader, database, id_book)
    collection_book.update_one({"_id": id_book}, {"$set": {'status': "reading"}})
    database.collection_user.update_one({"_id": int(id_user)}, {"$inc": {"count_book": 1}})

    return {"id_book": id_book}



@app.route('/get_book', methods=['POST'])
def get_book():
    global database
    data = request.get_json()
    print("Received data in get_book:", data)
    try:
        id_user = int(data['id_user'])
        id_book = int(data['id_book'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'Invalid user or book ID'}), 400
    
    user_data = database.collection_user.find_one({"_id": id_user})
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    
    user_books = user_data.get('book_id', [])
    if id_book not in user_books:
        return jsonify({'error': 'Book not found for user'}), 404
    
    document_book, collection_book = BD.init_book(id_book)
    if not document_book:
        return jsonify({'error': 'Book document not found'}), 404
    
    database.collection_book = collection_book
    
    # Возвращаем 'book_id' в ответе
    return jsonify({
        'book_id': id_book,
        'title': document_book['title'],
        'author': document_book['author'],
        'description': document_book['description']
    }), 200


@app.route('/change_mode', methods=['POST'])
def change_mode():
    global book_reader, questions, answer_user, database
    data = request.json
    try:
        id_user = int(data['id_user'])
        id_book = int(data['id_book'])
        mode = data['mode']
    except (ValueError, TypeError, KeyError):
        return jsonify({"error": "Invalid input data"}), 400

    # Проверяем, существует ли пользователь
    user_data = database.collection_user.find_one({"_id": id_user})
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    # Проверяем, принадлежит ли книга пользователю
    user_books = user_data.get('book_id', [])
    if id_book not in user_books:
        return jsonify({"error": "Book not found for user"}), 404

    # Инициализируем коллекцию книги
    document_book, collection_book = BD.init_book(id_book)
    if not document_book:
        return jsonify({"error": "Book document not found"}), 404

    database.collection_book = collection_book

    text = ''

    if mode == 'summarization_time' or mode == 'summarization':
        executor.submit(Summarize.process_chunk, book_reader, mode, database, id_book)
        database.collection_book.update_one({"_id": id_book}, {"$set": {"mode": mode}})
        database.collection_book.update_one({"_id": id_book}, {"$set": {"count_ready_block": 3}})
    elif mode == 'questions_original_text':
        database.collection_book.update_one({"_id": id_book}, {"$set": {"mode": mode}})
    elif mode == 'retelling':
        text = database.collection_book.find_one({"_id": id_book}).get('retelling', '')
    elif mode == 'test':
        questions_all, right_answers_all = questions.questions_all_book(database, id_book)
        return jsonify({"questions": questions_all, "right_answers": right_answers_all}), 200
    elif mode == 'similar_books':
        text = database.collection_book.find_one({"_id": id_book}).get('advice', '')
    else:
        return jsonify({"error": "Invalid mode"}), 400

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
    questions_list, right_answers = Questions_original_text.question_orig(book_reader, questions, answer_user, database,
                                                                     id_block, id_book)
    return jsonify({"questions": questions_list,
                    "right_answers": right_answers}), 200


@app.route('/get_text', methods=['POST'])
def get_text():
    global book_reader, questions, answer_user, database
    data = request.get_json()
    print("Received data in get_text:", data)

    try:
        id_user = int(data['id_user'])
        id_book = int(data['id_book'])
        print(f"id_user: {id_user}, id_book: {id_book}")
    except (ValueError, TypeError, KeyError) as e:
        print(f"Error parsing id_user or id_book: {e}")
        return jsonify({"error": "Invalid user or book ID"}), 400

    # Проверяем, существует ли пользователь
    user_data = database.collection_user.find_one({"_id": id_user})
    if not user_data:
        print(f"User with ID {id_user} not found")
        return jsonify({"error": "User not found"}), 404
    else:
        print(f"User data: {user_data}")

    # Проверяем, принадлежит ли книга пользователю
    user_books = user_data.get('book_id', [])
    print(f"User books: {user_books}")
    if id_book not in user_books:
        print(f"Book with ID {id_book} not found for user {id_user}")
        return jsonify({"error": "Book not found for user"}), 404
    else:
        print(f"Book with ID {id_book} belongs to user {id_user}")

    # Инициализируем коллекцию книги
    document_book, collection_book = BD.init_book(id_book)
    if not document_book:
        print(f"Book document with ID {id_book} not found")
        return jsonify({"error": "Book document not found"}), 404
    else:
        print(f"Document book: {document_book}")

    database.collection_book = collection_book
    
    name_file = document_book['name_file']
    # Получаем полное имя файла
    filename = os.path.basename(name_file)
    # Формируем полный путь к файлу
    name_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    name_file = os.path.abspath(name_file)

    print(f"Book file path: {name_file}")
    if not os.path.exists(name_file):
        print(f"File {name_file} not found")
        return jsonify({'error': f"File {name_file} not found"}), 404
    else:
        print(f"File {name_file} exists")

    mode = document_book.get('mode', 'summarization')
    print(f"Book mode: {mode}")

    # Инициализируем необходимые объекты
    book_reader, questions, answer_user, chapters = initialize.init_objects(name_file)
    collection_text = BD.init_text()
    database.collection_text = collection_text

    text = ""
    id_block = 0

    if mode == 'summarization_time':
        executor.submit(Summarize.process_chunk, book_reader, 'time', database, id_book)
        text, id_block, reading_time = Summarize.process_text(name_file, book_reader, 'time', database, id_book)
    elif mode == 'summarization':
        executor.submit(Summarize.process_chunk, book_reader, 'sum', database, id_book)
        text, id_block, reading_time = Summarize.process_text(name_file, book_reader, 'sum', database, id_book)
    elif mode == 'questions_original_text':
        text, id_block = Questions_original_text.get_text(book_reader, questions, answer_user, database, id_book)
    else:
        text = "No valid mode selected."
        id_block = 0
        print("No valid mode selected")

    print(f"Returning text of length {len(text)} and id_block {id_block}")
    return jsonify({"text": text, "id_block": id_block}), 200


@app.route('/next_block_text', methods=['POST'])
def next_block_text():
    data = request.json
    try:
        id_user = int(data['id_user'])
        id_book = int(data['id_book'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user or book ID"}), 400

    # Проверяем, существует ли пользователь
    user_data = database.collection_user.find_one({"_id": id_user})
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    # Проверяем, принадлежит ли книга пользователю
    user_books = user_data.get('book_id', [])
    if id_book not in user_books:
        return jsonify({"error": "Book not found for user"}), 404

    # Инициализируем коллекцию книги
    document_book, collection_book = BD.init_book(id_book)
    if not document_book:
        return jsonify({"error": "Book document not found"}), 404

    database.collection_book = collection_book

    block_stop = document_book.get('block_stop_book', 0)
    count_block = len(document_book.get('id_text', []))
    if block_stop + 1 < count_block:
        database.collection_book.update_one({"_id": id_book}, {"$inc": {"block_stop_book": 1}})

    return jsonify({"message": "Moved to next block"}), 200


@app.route('/back_block_text', methods=['POST'])
def back_block_text():
    data = request.json
    try:
        id_user = int(data['id_user'])
        id_book = int(data['id_book'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user or book ID"}), 400

    # Проверяем, существует ли пользователь
    user_data = database.collection_user.find_one({"_id": id_user})
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    # Проверяем, принадлежит ли книга пользователю
    user_books = user_data.get('book_id', [])
    if id_book not in user_books:
        return jsonify({"error": "Book not found for user"}), 404

    # Инициализируем коллекцию книги
    document_book, collection_book = BD.init_book(id_book)
    if not document_book:
        return jsonify({"error": "Book document not found"}), 404

    database.collection_book = collection_book

    block_stop = document_book.get('block_stop_book', 0)
    if block_stop > 0:
        database.collection_book.update_one({"_id": id_book}, {"$inc": {"block_stop_book": -1}})
        database.collection_book.update_one({"_id": id_book}, {"$inc": {"count_ready_block": 1}})

    return jsonify({"message": "Moved to previous block"}), 200


# back button
# баг вопросы
# считывание книги сделать
# отладит код
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
