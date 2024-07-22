import Summarize
import Questions
import os
import ParserFB2
import Divide
import about_book
import Answer_user
import BookReader
import Questions_original_text
from flask import Flask, request, jsonify
from pymongo import MongoClient
from Scripts import Divide, BookReader, Questions, Answer_user


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
      file_name, file_exp = os.path.splitext(f"C:/Users/miros/PycharmProjects/BookAI/Scripts/{name_file}")
      if file_exp == ".fb2":
            file_name = ParserFB2.process_fb2(name_file)
            return file_name
      if file_exp == ".txt":
            return name_file
      return None

def main(name_file):
      name_file = check_extension(name_file)
      if name_file is None:
            print("Other format book\n")
      chapters = Divide.split_book_by_chapters(name_file)
      book_reader = BookReader.BookReader(name_file)
      questions = Questions.Questions(name_file)
      answer_user = Answer_user.User_Answer("", count_answer=4, block_text=3000)
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
                  Summarize.control(name_file, questions, answer_user, book_reader)
            if answer == 2:
                  if book_reader.number_chapter >= len(chapters):
                        questions = Questions.Questions(name_file)
                        answer_user = Answer_user.User_Answer("", count_answer=4, block_text=3000)
                  Questions_original_text.question_orig(book_reader, questions, answer_user)
            if answer == 3:
                  about_book.retelling(name_file, chapters, questions, answer_user, book_reader)
            if answer == 4:
                  about_book.about_book(chapters)
            if answer == 5:
                  if len(questions.right_answer) == 0:
                        print("Read first\n")
                  else:
                        questions.questions_all_book()
            if answer == 6:
                  about_book.advice_book(chapters)
            if answer == 7:
                  break
main(name_file)

