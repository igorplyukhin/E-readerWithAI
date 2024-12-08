from flask import request, jsonify
from fastapi import APIRouter
from pymongo import MongoClient
from bson import ObjectId
from utils.BackgroundProcessing import BackgroundProcessing

text_router = APIRouter()
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']

@text_router.route('/get_text', methods=['POST'])
def get_text():
    id_user = request.form.get('id_user')
    id_book = request.form.get('id_book')

    if not id_user or not id_book:
        return jsonify({"error": "ID пользователя или книги не предоставлен"}), 400

    books_collection = db.books
    book_doc = books_collection.find_one({"_id": ObjectId(id_book), "userId": id_user})

    if not book_doc:
        return jsonify({"error": "Книга не найдена или не принадлежит пользователю"}), 404

    current_block_index = book_doc['blockStopBook']
    id_block = book_doc['textBlockIds'][current_block_index] if current_block_index < len(book_doc['textBlockIds']) else None

    if not id_block:
        return jsonify({"error": "Текстовый блок не найден"}), 404

    text_blocks_collection = db.text_blocks
    text_block_doc = text_blocks_collection.find_one({"_id": ObjectId(id_block)})

    if not text_block_doc:
        return jsonify({"error": "Текстовый блок не найден"}), 404

    mode = book_doc['mode']

    if mode == "summarization_time":
        if text_block_doc.get('summaryTime') is None:
            BackgroundProcessing.process_summarization_for_block(text_block_doc, mode="summarization_time")
            return jsonify({"message": "Суммирование с учетом времени чтения запущено. Попробуйте позже."}), 202
        else:
            return jsonify({"text": text_block_doc['summaryTime'], "id_block": str(id_block)})
    elif mode == "summarization":
        if text_block_doc.get('summary') is None:
            BackgroundProcessing.process_summarization_for_block(text_block_doc, mode="summarization")
            return jsonify({"message": "Суммирование запущено. Попробуйте позже."}), 202
        else:
            return jsonify({"text": text_block_doc['summary'], "id_block": str(id_block)})
    elif mode == "questions_original_text":
        return jsonify({"text": text_block_doc['original'], "id_block": str(id_block)})
    else:
        return jsonify({"error": "Неверный режим книги"}), 400

@text_router.route('/get_questions', methods=['POST'])
def get_questions():
    id_user = request.form.get('id_user')
    id_book = request.form.get('id_book')
    id_block = request.form.get('id_block')

    if not id_user or not id_book or not id_block:
        return jsonify({"error": "Не предоставлены необходимые параметры"}), 400

    books_collection = db.books
    book_doc = books_collection.find_one({"_id": ObjectId(id_book), "userId": id_user})

    if not book_doc:
        return jsonify({"error": "Книга не найдена или не принадлежит пользователю"}), 404

    text_blocks_collection = db.text_blocks
    text_block_doc = text_blocks_collection.find_one({"_id": ObjectId(id_block)})

    if not text_block_doc:
        return jsonify({"error": "Текстовый блок не найден"}), 404

    if not text_block_doc.get('questions'):
        questions, answers = BackgroundProcessing.generate_questions_for_block(text_block_doc['original'])
        text_blocks_collection.update_one(
            {"_id": ObjectId(id_block)},
            {"$set": {"questions": questions, "rightAnswers": answers}}
        )
        return jsonify({"questions": questions, "answers": answers})
    else:
        return jsonify({"questions": text_block_doc['questions'], "answers": text_block_doc['rightAnswers']})

@text_router.route('/next_block_text', methods=['POST'])
def next_block_text():
    id_user = request.form.get('id_user')
    id_book = request.form.get('id_book')

    if not id_user or not id_book:
        return jsonify({"error": "ID пользователя или книги не предоставлен"}), 400

    books_collection = db.books
    book_doc = books_collection.find_one({"_id": ObjectId(id_book), "userId": id_user})

    if not book_doc:
        return jsonify({"error": "Книга не найдена или не принадлежит пользователю"}), 404

    next_block_index = book_doc['blockStopBook'] + 1
    if next_block_index >= len(book_doc['textBlockIds']):
        return jsonify({"error": "Это последний блок текста"}), 400

    books_collection.update_one(
        {"_id": ObjectId(id_book)},
        {"$set": {"blockStopBook": next_block_index}}
    )
    return jsonify({"message": "Переход к следующему блоку выполнен"})

@text_router.route('/back_block_text', methods=['POST'])
def back_block_text():
    id_user = request.form.get('id_user')
    id_book = request.form.get('id_book')

    if not id_user or not id_book:
        return jsonify({"error": "ID пользователя или книги не предоставлен"}), 400

    books_collection = db.books
    book_doc = books_collection.find_one({"_id": ObjectId(id_book), "userId": id_user})

    if not book_doc:
        return jsonify({"error": "Книга не найдена или не принадлежит пользователю"}), 404

    previous_block_index = book_doc['blockStopBook'] - 1
    if previous_block_index < 0:
        return jsonify({"error": "Это первый блок текста"}), 400

    books_collection.update_one(
        {"_id": ObjectId(id_book)},
        {"$set": {"blockStopBook": previous_block_index}}
    )
    return jsonify({"message": "Переход к предыдущему блоку выполнен"})

if __name__ == '__main__':
    text_router.run(debug=True)

