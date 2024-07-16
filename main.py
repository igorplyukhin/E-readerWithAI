import Summarize
import Questions
import os
import ParserFB2
import Divide
import about_book


name_file = "72963.fb2"


def help():
    print(f'1. Читать книгу с ограничением по времени\n'
          f'2. Читать с вопросами\n'
          f'3. Читать пересказ книги\n'
          f'4. О чем книга\n'
          f'5. Пройти тест по всей книге\n')


def check_extension(name_file):
      file_name, file_exp = os.path.splitext(f"C:/Users/miros/PycharmProjects/BookAI/{name_file}")
      if file_exp == ".fb2":
            file_name = ParserFB2.process_fb2(name_file)
            return file_name
      return None


def divide_text(name_file):
      chapters = Divide.split_book_by_chapters(name_file)

name_file = check_extension(name_file)
if name_file is None:
      print("=(")


questions = Questions.Questions(name_file)
while True:
      help()
      answer = input("... ")
      answer = int(answer)
      if answer not in range(1, 7):
            while answer not in range(1, 7):
                  answer = input("... ")
                  answer = int(answer)
      if answer == 1:
            Summarize.control(name_file)
      if answer == 2:
            questions = Questions.Questions(name_file)
            questions.create_questions()
      if answer == 3:
            about_book.retelling(name_file)
      if answer == 4:
            about_book.about_book(name_file)
      if answer == 5:
            if len(questions.right_answer) == 0:
                  print("Прочитай сначала\n")
            else:
                  questions.questions_all_book()


