import LLaMA
import BookReader
import shutil



def summarize_at_time(name_file, name_sum_file):
    day = int(input("Количество дней:"))
    hours_in_day = float(input("Часов в день:"))
    if (day <= 0 or hours_in_day <= 0):
        print("Некорректные значения\n")
        return summarize_at_time(name_file)
    time = day*hours_in_day*60
    speed_reading = 200
    count_symbols_user = time * speed_reading
    book = open(name_file, "r", encoding="utf-8")
    length = len(book.read())
    book.close()
    book_reader = BookReader.BookReader(name_file)
    if count_symbols_user >= length:
        print("За указанное время вы прочтёте книгу полностью!")
        answer = input("Изменить время?(y/n):")
        if answer == 'y':
            return summarize_at_time(name_file, name_sum_file)
        else:
            return
    precent_sum = count_symbols_user / length
    count_symbols_sum = round(precent_sum*book_reader.block_text)
    book_reader = BookReader.BookReader(name_file)
    while length > count_symbols_user:
        with open(book_reader.name_file, 'r', encoding='utf-8') as book:
            while book_reader.end_file:
                book_reader.read_block(book)
                if book_reader.count_symbols == book_reader.block_text:
                    book_reader.read_until_paragraph(book)
                result = LLaMA.llama(book_reader.data, "sum at time", count_symbols_sum)
        book.close()

name_file = "book.txt"
name_sum_file2 = "SummarizeAtTime2.txt"
name_sum_file = "SummarizeAtTime.txt"
shutil.copy('book.txt', "SummarizeAtTime.txt")
summarize_at_time(name_sum_file,name_sum_file2)