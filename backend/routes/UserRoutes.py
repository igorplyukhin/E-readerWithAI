from flask import Flask, request, jsonify
from fastapi import APIRouter
from pymongo import MongoClient
from bson import ObjectId
import os

user_router = APIRouter()

# Assuming DatabaseFactory is replaced with a direct MongoDB connection
client = MongoClient(os.environ.get('MONGODB_URI', 'mongodb://localhost:27017'))
db = client['your_database_name']

def get_users_collection():
    return db['users']

def get_books_collection():
    return db['books']

@user_router.route('/get_user', methods=['POST'])
def get_user():
    login = request.form.get('login')

    if not login:
        return jsonify({"error": "Логин не предоставлен"}), 400

    users_collection = get_users_collection()
    user_doc = users_collection.find_one({"_id": login})

    if user_doc:
        user = user_doc  # Assuming toUser() is not needed in Python
        if user.get('bookIds'):
            books_collection = get_books_collection()
            object_id_list = [ObjectId(book_id) for book_id in user['bookIds']]
            books = list(books_collection.find({"_id": {"$in": object_id_list}}))

            response = {
                "count_book": len(books),
                "books": books
            }
            return jsonify(response)
        else:
            return jsonify({"count_book": 0, "books": []})
    else:
        return jsonify({"error": "Пользователь не найден"}), 404

@user_router.route('/register', methods=['POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return jsonify({"status": "error", "message": "Логин или пароль не предоставлены"}), 400

    users_collection = get_users_collection()
    existing_user = users_collection.find_one({"_id": login})

    if existing_user:
        return jsonify({"status": "error", "message": "Пользователь с таким логином уже существует"}), 409

    new_user = {"_id": login, "password": password}
    users_collection.insert_one(new_user)

    return jsonify({"status": "success", "message": "Пользователь успешно зарегистрирован", "userId": login}), 201

@user_router.route('/login', methods=['POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return jsonify({"status": "error", "message": "Логин или пароль не предоставлены"}), 400

    users_collection = get_users_collection()
    user_doc = users_collection.find_one({"_id": login})

    if user_doc:
        if user_doc['password'] == password:
            return jsonify({"status": "success", "message": "Аутентификация успешна", "userId": login})
        else:
            return jsonify({"status": "error", "message": "Неверный пароль"}), 401
    else:
        return jsonify({"status": "error", "message": "Пользователь не найден"}), 404

@user_router.route('/update_user', methods=['POST'])
def update_user():
    login = request.form.get('login')
    new_password = request.form.get('new_password')
    old_password = request.form.get('old_password')

    if not login or not new_password or not old_password:
        return jsonify({"error": "Не предоставлены необходимые параметры"}), 400

    users_collection = get_users_collection()
    user_doc = users_collection.find_one({"_id": login})

    if user_doc and user_doc['password'] == old_password:
        result = users_collection.update_one(
            {"_id": login},
            {"$set": {"password": new_password}}
        )

        if result.modified_count > 0:
            return jsonify({"message": "Пароль успешно обновлен"})
        else:
            return jsonify({"error": "Не удалось обновить пароль"}), 500
    else:
        return jsonify({"error": "Старый пароль неверен или пользователь не найден"}), 401

@user_router.route('/delete_user', methods=['POST'])
def delete_user():
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return jsonify({"error": "Логин или пароль не предоставлен"}), 400

    users_collection = get_users_collection()
    user_doc = users_collection.find_one({"_id": login})

    if user_doc and user_doc['password'] == password:
        result = users_collection.delete_one({"_id": login})

        if result.deleted_count > 0:
            return jsonify({"message": "Пользователь успешно удален"})
        else:
            return jsonify({"error": "Не удалось удалить пользователя"}), 500
    else:
        return jsonify({"error": "Неверный пароль или пользователь не найден"}), 401

if __name__ == '__main__':
    user_router.run(debug=True)

