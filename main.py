import Summarize
import Questions
number = "ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ"
symbols = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV"]
name_file = "book.txt"
name_sum_file = "SummaryBook.txt"
Summarize.summarize(name_file, name_sum_file)
Questions.create_questions(name_file)
#сot