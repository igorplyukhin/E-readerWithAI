from flask import Flask, request, jsonify
from pymongo import MongoClient
from Scripts import Divide, BookReader, Questions, Answer_user

app = Flask(__name__)

# Настройка подключения к MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']  # Имя базы данных
collection = db['users']  # Имя коллекции для хранения сессий
collection.delete_many({})
data = {"_id": 1,
        "login": "user777"}
book_id = {"book_id_1": 1}
book_id_1 = {"book_id_1": 2}
block_stop_book = {"block_stop_book_1": 1}
chapter_stop_book = {"chapter_stop_book_1": 1}
collection.insert_one(data)
collection.update_one({"_id": 1}, {"$set": book_id})
collection.update_one({"_id": 1}, {"$set": book_id_1})

collection_book = db['user_book_1']
collection_book.delete_many({})

data = {"_id": 1}
collection_book.insert_one(data)
collection_book.update_one({"_id": 1}, {"$set": block_stop_book})
collection_book.update_one({"_id": 1}, {"$set": chapter_stop_book})
login = "user777"
document = collection.find_one({"login": "user777"})
user_id = document["_id"]
book_id = document["book_id_1"]

collection_text = db[f'user_{user_id}_book_{book_id}_text']
collection_text.delete_many({})

str = open("book.txt", "r", encoding="utf-8").read()
print("sd")
for i in range(1, 1000):
    new_data = {"_id": i,
            "Original": str,
            "Sum": str,
            "Sum_time": str,
            "Question_1": "str",
            "Question_2": "str",
            "Right_answer_1": 3,
            "Right_answer_2": 3
            }
    collection_text.insert_one(new_data)