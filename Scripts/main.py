import Summarize
import Questions
import os
import ParserFB2
import Divide
import informs_book
import Answer_user
import BookReader
import Questions_original_text
from flask import Flask, request, jsonify
from pymongo import MongoClient
from Scripts import Divide, BookReader, Questions, Answer_user
import BD
from pymongo import MongoClient

name_file = "book.txt"

def help():
    print(f'1. Read the summarized version\n'
          f'2. Read with questions\n'
          f'3. Read the retelling of the book\n'
          f'4. About the book\n'
          f'5. Take a test on the book\n'
          f'6. Similar books\n'
          f'7. Exit')  # Enum

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
      book_reader = BookReader.BookReader(name_file)
      questions = Questions.Questions(name_file)
      answer_user = Answer_user.User_Answer("", count_answer=4)

      return book_reader, questions, answer_user, chapters


def information(chapters, questions, answer_user, book_reader):
      title, author = informs_book.title_book(chapters)
      information_book = {
            "name_file": questions.name_file,
            "about": informs_book.about_book(chapters, title + ' ' + author),
            "retelling": informs_book.retelling(name_file, chapters, questions, answer_user, book_reader,
                                                title + ' ' + author),
            "advice": informs_book.advice_book(chapters, title + ' ' + author),
            "title": title,
            "author": author
      }  # Оптимизация
      return information_book


def interface(book_reader, questions, answer_user, chapters,  database):
      while True:
            book_reader.flag_break = False
            help()
            answer = input("comand: ")
            while not answer.isdigit():
                  print("Incorrect input\n")
                  answer = input("comand: ")
            answer = int(answer)
            if answer not in range(1, 8):
                  while answer not in range(1, 8):
                        answer = input("comand: ")
                        answer = int(answer)
            if answer == 1:
                  Summarize.control(name_file, questions, answer_user, book_reader, database)
            if answer == 2:
                  if book_reader.number_chapter >= len(chapters):
                        questions = Questions.Questions(name_file)
                        answer_user = Answer_user.User_Answer("", count_answer=4)
                  Questions_original_text.question_orig(book_reader, questions, answer_user, database)
            if answer == 3:
                  print(database.collection_book.find_one({"_id": database.id_book})['retelling'])
            if answer == 4:
                  print(database.collection_book.find_one({"_id": database.id_book})['description'])
            if answer == 5:
                  if database.collection_text.count_documents({}) == 0:
                        print("Read first\n")
                  else:
                        questions.questions_all_book(database)
            if answer == 6:
                  print(database.collection_book.find_one({"_id": database.id_book})['advice'])
            if answer == 7:
                  break


def init_user(login):
      document_user, collection_user = BD.init_user(login)
      database = BD.Database(collection_user, {}, {}, document_user['_id'], 0)
      return database


def init_documents(login, chapters, questions, answer_user, book_reader):
      document_user, collection_user = BD.init_user(login)
      # возвращаем id книг
      # получаем id книги или создаем
      id_book = document_user['count_book'] + 1
      document_book, collection_book = BD.init_book(id_book)
      if document_book is None:
            information_book = information(chapters, questions, answer_user, book_reader)
            document_book, collection_book = BD.create_book(id_book, information_book, document_user['_id'])
      collection_text = BD.init_text()
      user_id = document_user['_id']
      book_id = document_book['_id']

      database = BD.Database(collection_user, collection_book, collection_text, user_id, book_id)
      return database

def main(name_file):
      login = "user777"
      database = init_user(login)
      if len(database.collection_user.find_one({'_id': database.id_user})['book_id']) != 0:
            print(database.collection_user.find_one({'_id': database.id_user})['book_id'])
      id_book = 1 #получаем от пользователя
      document_book, collection_book = BD.init_book(id_book)
      if document_book is None:
            name_file = name_file  # достаем название файла из json
            book_reader, questions, answer_user, chapters = init_objects(name_file)
            information_book = information(chapters, questions, answer_user, book_reader)
            document_book, collection_book = BD.create_book(id_book, information_book, database.id_user)
            database.collection_user.update_one({'_id': database.id_user},
                                            {"$push": {"book_id": id_book}})
            database.collection_user.update_one({'_id': database.id_user},
                                                {"$inc": {"count_book": 1}})
      else:
            name_file = document_book['name_file']
            book_reader, questions, answer_user, chapters = init_objects(name_file)
      collection_text = BD.init_text()
      database.id_book = id_book
      database.collection_text = collection_text
      database.collection_book = collection_book
      # book_reader, questions, answer_user, chapters = init_objects(name_file)
      # database = init_documents(login, chapters, questions, answer_user, book_reader)
      interface(book_reader, questions, answer_user, chapters, database)


main(name_file)

# хранить ли главы?