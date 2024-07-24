import LLaMA
import concurrent.futures
import Divide
import asyncio
import time


# Функция для суммаризации книги и записи результатов в файл
def summarize(name_file, name_sum_file, need_questions, questions, answer, book_reader):
    print("Processing your text =)...")
    encoding = book_reader.detect_encoding()
    chapters = Divide.split_book_by_chapters(name_file)
    SummaryBook = open(name_sum_file, "w", encoding=encoding)
    number_chapter = 0
    while number_chapter < len(chapters):
        if len(chapters[number_chapter]) < 200:
            number_chapter += 1
            continue
        number_chapter = book_reader.reading(chapters, number_chapter)
        book_reader.block_original.append(book_reader.data) # bd
        summary = LLaMA.llama(book_reader.data, "sum", 0, 0, 0)
        summary_edit = LLaMA.llama(summary, "edit", 0, 0, 0)
        print(summary_edit + "\n")
        input("")
        if need_questions is True:
            questions.create_questions(summary_edit, answer, book_reader)
        SummaryBook.write(summary_edit)
        SummaryBook.write("\n")
        book_reader.data = ""
    questions.right_answer = answer.right_answer
    SummaryBook.close()


# Функция для получения длины книги
def len_book(name_file):
    encoding = Divide.detect_encoding(name_file)
    book = open(name_file, "r", encoding=encoding)
    length = len(book.read())
    book.close()
    return length


def count_sentences(text):
    count = 0
    for i in range(len(text)):
        if text[i] == '.':
            count += 1
    return count


# Асинхронная функция для обработки частей книги
def process_chunk(book_reader,  mode, database):
    if database.collection_book.find_one({"_id": database.id_book})['stop_process'] == 0:
        number_block = 3
    else:
        number_block = database.collection_book.find_one({"_id": database.id_book})['stop_process']
    while True:
        if book_reader.flag_break is True:
            break
        if number_block < len(database.collection_book.find_one({'_id': database.id_book})['id_text']):
            while book_reader.count_ready_block == 3:
                if book_reader.flag_break is True:
                    break
                time.sleep(1)  # Ожидание если достигнут лимит готовых блоков
            id_block = database.collection_book.find_one({'_id': database.id_book})['id_text'][number_block]
            text = database.collection_text.find_one({'_id': id_block})['original']
            length = count_sentences(text)
            if mode == 'time':
                summary = LLaMA.llama(text, "sum at time", book_reader.symbols_koef * length, 0, 0)
            if mode == 'sum':
                summary = LLaMA.llama(text, "sum", 0, 0, 0)
            summary_edit = LLaMA.llama(summary, "edit", 0, 0, 0)
            if mode == "time":
                database.add_sum_time_text(summary_edit, id_block)
            if mode == 'sum':
                database.add_sum_text(summary_edit, id_block)
            book_reader.count_ready_block += 1
            number_block += 1
            database.collection_book.update_one({"_id": database.id_book}, {"$set": {"stop_process": number_block}})
            book_reader.data = ""
        else:
            break


# Главная асинхронная функция для управления процессом чтения и суммаризации
async def main(name_file, need_questions, questions, answer_user, book_reader, mode, database):
    book_reader.flag_break = False
    length_book = len_book(name_file)  # Получение длины книги
    if mode == 'time':
        days = int(input("Enter the number of days: "))
        hours = float(input("Enter the number of hours per day: "))
        time_full = days * hours * 60  # Полное время для чтения (в минутах)
    if database.collection_book.find_one({'_id': database.id_book})['status'] == 'start':
        chapters = Divide.split_book_by_chapters(name_file)  # Разделение книги на главы
        text = Divide.split_chapters(chapters, book_reader, database)
        database.collection_book.update_one({"_id": database.id_book}, {"$set": {'status': "reading"}})
    book_reader.count_block = database.collection_book.find_one({"_id": database.id_book})['block_stop_book']
    if book_reader.count_block >= len(database.collection_book.find_one(
            {'_id': database.id_book})['id_text']):
        #
        return
    # Начальная обработка первых трех глав
    book_reader.count_ready_block = 3
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(process_chunk, book_reader, mode, database)
        flag = 1
        # Основной цикл обработки и взаимодействия с пользователем
        while book_reader.count_block < len(database.collection_book.find_one({'_id': database.id_book})['id_text']):

            length_blocks = 0
            time_blocks = 0
            if book_reader.count_ready_block >= 1:
                flag = 1
                start = time.time()
                id_text = database.collection_book.find_one({"_id": database.id_book})['id_text']
                id_block = id_text[book_reader.count_block]
                if book_reader.count_block < 3:
                    text = database.collection_text.find_one({"_id": id_block})['original']
                # print(f"\n{arr_block[book_reader.count_block]}")
                else:
                    if mode == "sum":
                        text = database.collection_text.find_one({"_id": id_block})['sum']
                    if mode == "time":
                        text = database.collection_text.find_one({"_id": id_block})['sum_time']
                print(text)
                if need_questions is True:
                    questions.create_questions(text, answer_user, book_reader, database, id_block)  # bd
                book_reader.count_ready_block -= 1
                answer = ''
                answer = input("Press Enter to continue, type 'original', 'exit', 'edit' for further processing...")
                count_iter = 0
                if answer == "exit":
                    print("Ending the process =)...\n")
                    book_reader.flag_break = True
                    break
                if answer == "original":
                    print(book_reader.block_original[book_reader.count_block]) #bd
                while answer == "edit":
                    if count_iter == 4:
                        print(book_reader.block_original[book_reader.count_block]) #bd
                        break
                    print("Please wait...\n")
                    result = LLaMA.llama(book_reader.block_original[book_reader.count_block], "sum at time", count_sentences(book_reader.block_original[book_reader.count_block]) * book_reader.symbols_koef, 0, 0) # bd
                    print(result)
                    answer = input("Press Enter to continue or 'edit' for further processing...")
                end = time.time()
                reading_time = (end - start) / 60
                if mode == "sum":
                    book_reader.count_block += 1
                    continue
                if reading_time > 30:
                    reading_time = 15
                book_reader.reading_times.append(reading_time)  #bd
                if book_reader.count_block >= 3:
                    for i in range(1, 4):
                        id_block = id_text[book_reader.count_block - i]
                        if mode == "sum":
                            text = database.collection_text.find_one({"_id": id_block})['sum']
                        if mode == "time":
                            text = database.collection_text.find_one({"_id": id_block})['sum_time']
                        length_blocks += len(text)
                        time_blocks += book_reader.reading_times[book_reader.count_block - i]
                    speed_reading = length_blocks / time_blocks
                    time_orig = length_book / speed_reading
                    if time_orig <= time_full:
                        print("You will read the book in the original in this time and at this reading speed")
                        book_reader.symbols_koef = 1
                    else:
                        book_reader.symbols_koef = time_full / time_orig
                if mode == "time":
                    print(f"Reading time of fragment {book_reader.count_block + 1}: {reading_time:.2f} minutes\n")
                    print(f'Compression coefficient - {book_reader.symbols_koef}\n')
                book_reader.count_block += 1
            else:
                if flag == 1:
                    print("Please wait, the fragment is not processed yet.")
                flag = 0
                time.sleep(1)
    database.add_block_stop(book_reader.count_block)  # запомним фрагмент на котором остановился читатель
    database.add_chapter_stop(book_reader.number_chapter)
    if mode == "time":
        print(f"Total reading time: {sum( book_reader.reading_times): .2f} minutes")


def control(name_file, questions, answer, book_reader, database):
    name_sum_file = "SummaryBook.txt"
    need_questions = input("Do you need questions? (yes/no): ")
    while need_questions != "yes" and need_questions != "no":
        need_questions = input("Do you need questions? (yes/no): ")
    if need_questions == "yes":
        need_questions = True
    else:
        need_questions = False
    mode = input("Read in time or randomly summarized text(time/sum): ")
    while mode != "time" and mode != "sum":
        mode = input("Read in time or randomly summarized text(time/sum): ")
    if mode == "time":
        asyncio.run(main(name_file, need_questions, questions, answer, book_reader, "time", database))
    if mode == "sum":
        asyncio.run(main(name_file, need_questions, questions, answer, book_reader, "sum", database))
