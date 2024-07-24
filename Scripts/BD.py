from flask import Flask, request, jsonify
from pymongo import MongoClient
from Scripts import Divide, BookReader, Questions, Answer_user


class Database:

        def __init__(self, collection_user, collection_book, collection_text, id_user: int, id_book: int):
                self.collection_book = collection_book
                self.collection_user = collection_user
                self.collection_text = collection_text
                self.id_user = id_user
                self.id_book = id_book
                self.current_block_id = 0

        def new_block(self):
            id_block = self.collection_text.count_documents({}) + 1
            data = {"_id": id_block}
            self.collection_text.insert_one(data)
            return id_block

        def add_original_text(self, text, id_text):
                original_text = {"original": text}
                self.collection_text.update_one({"_id": id_text}, {"$set": original_text})

        def add_sum_text(self, summary, id_block):
                summary = {"sum": summary}
                self.collection_text.update_one({"_id": id_block}, {"$set": summary})

        def add_sum_time_text(self, sum_time, id_block):
                summary_time = {"sum_time": sum_time}
                self.collection_text.update_one({"_id": id_block}, {"$set": summary_time})

        def add_question(self, question):
                self.collection_text.update_one({"_id": self.current_block_id}, {"$push": {"questions": question}})

        def add_right_answer(self, right_answer, id_block):
                self.collection_text.update_one({"_id": id_block}, {"$push": {"right_answers": right_answer}})

        def add_id_book(self, id_block):
                self.collection_book.update_one({'_id': self.id_book},
                                            {"$push": {"id_text": id_block}})

        def add_block_stop(self, block_stop: int):
                self.collection_book.update_one({"_id": self.id_book}, {"$set": {"block_stop_book": block_stop}})

        def add_chapter_stop(self, chapter_stop: int):
                self.collection_book.update_one({"_id": self.id_book}, {"$set": {"chapter_stop_book": chapter_stop}})

        def number_chapter(self, number_chapter: int, id_text: int):
                self.collection_text.update_one({"id": id_text}, {"$set": {"number_chapter": number_chapter}})

def create_document(login):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mydatabase']  # Имя базы данных
        collection = db['users']  # Имя коллекции для хранения сессий
        new_user_id = collection.count_documents({}) + 1
        data = {"_id": 1,
                "login": login}
        count_book = {"count_book": 0}
        book_id = {"book_id": []}

        collection.insert_one(data)
        collection.update_one({"_id": 1}, {"$set": count_book})
        collection.update_one({"_id": 1}, {"$set": book_id})
        document = collection.find_one({"login": login})
        return document


def init_user(login):
        # Настройка подключения к MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mydatabase']  # Имя базы данных
        collection = db['users']  # Имя коллекции для хранения сессий
        #collection.delete_many({})  # !!!!!
        document = collection.find_one({"login": login})
        if document is None:
                answer = input("Create account?(y/n): ")
                while answer != 'y' and answer != 'n':
                        answer = input("Create account?(y/n): ")
                if answer == 'y':
                        document = create_document(login)
        #collection.update_one({"_id": 1}, {"$inc": {"count_book": 1}})
        # collection.update_one(
        #         {"_id": 1},
        #         {"$push": {"book_id": 2}}
        # )
        return document, collection


def create_book(id_book, information, id_user):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mydatabase']  # Имя базы данных
        collection_book = db['user_book']
        data = {"_id": id_book}
        collection_book.insert_one(data)
        title = {"title": information['title']}
        block_stop_book = {"block_stop_book": 0}
        chapter_stop_book = {"chapter_stop_book": 0}
        author = {"author": information['author']}
        about_book = {"description": information['about']}
        advice = {"advice": information['advice']}
        retelling = {"retelling": information['retelling']}
        id_text = {"id_text": []}
        id_User = {"id_user": id_user}
        block_text = {"block_text": 3000}
        status = {"status": "start"}
        stop_process = {"stop_process": 0}

        collection_book.update_one({"_id": id_book}, {"$set": id_User})

        collection_book.update_one({"_id": id_book}, {"$set": title})

        collection_book.update_one({"_id": id_book}, {"$set": author})

        collection_book.update_one({"_id": id_book}, {"$set": about_book})

        collection_book.update_one({"_id": id_book}, {"$set": retelling})

        collection_book.update_one({"_id": id_book}, {"$set": advice})

        collection_book.update_one({"_id": id_book}, {"$set": id_text})

        collection_book.update_one({"_id": id_book}, {"$set": block_stop_book})

        collection_book.update_one({"_id": id_book}, {"$set": chapter_stop_book})

        collection_book.update_one({"_id": id_book}, {"$set": block_text})

        collection_book.update_one({"_id": id_book}, {"$set": status})

        collection_book.update_one({"_id": id_book}, {"$set": stop_process})

        document = collection_book.find_one({"_id": id_book})
        return document, collection_book


def init_book(id_book):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mydatabase']  # Имя базы данных
        collection_book = db['user_book']
        document = collection_book.find_one({"_id": id_book})
        return document, collection_book


def init_text():
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mydatabase']  # Имя базы данных
        collection_text = db['book_text']
        return collection_text
# collection_book = db['user_book_1']
# collection_book.delete_many({})
# id_book = 1  # Получаем с фронта
# data = {"_id": id_book}
# collection_book.insert_one(data)
# title = {"title": "Title book"}
# collection_book.update_one({"_id": id_book}, {"$set": title})
# Author = {"author": "Author book"}
# collection_book.update_one({"_id": id_book}, {"$set": Author})
# about_book = {"description": "description"}
# collection_book.update_one({"_id": id_book}, {"$set": about_book})
# retelling = {"retelling": "retelling"}
# collection_book.update_one({"_id": id_book}, {"$set": retelling})
# id_text = {"id_text": [1, 2, 3]}
# collection_book.update_one({"_id": id_book}, {"$set": id_text})
#
# collection_book.update_one({"_id": id_book}, {"$set": block_stop_book})
# collection_book.update_one({"_id": id_book}, {"$set": chapter_stop_book})
# login = "user777"
# document = collection.find_one({"login": "user777"})
# user_id = document["_id"]
# print(user_id)
# collection_text = db[f'user_{user_id}_book_{book_id}_text']
# collection_text.delete_many({})
#
# str = open("book.txt", "r", encoding="utf-8").read()
# print("sd")
# for i in range(1, 1000):
#     new_data = {"_id": i,
#             "Original": str,
#             "Sum": str,
#             "Sum_time": str,
#             "Question_1": "str",
#             "Question_2": "str",
#             "Right_answer_1": 3,
#             "Right_answer_2": 3
#             }
#     collection_text.insert_one(new_data)