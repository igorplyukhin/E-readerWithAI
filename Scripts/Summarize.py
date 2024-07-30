import LLaMA
import concurrent.futures
import Divide
import asyncio
import time


# Функция для суммаризации книги и записи результатов в файл
# def summarize(name_file, name_sum_file, need_questions, questions, answer, book_reader):
#     print("Processing your text =)...")
#     encoding = book_reader.detect_encoding(name_file)
#     file_path = f"uploads/{book_reader.name_file}"
#     chapters = Divide.split_book_by_chapters(file_path)
#     SummaryBook = open(name_sum_file, "w", encoding=encoding)
#     number_chapter = 0
#     while number_chapter < len(chapters):
#         if len(chapters[number_chapter]) < 200:
#             number_chapter += 1
#             continue
#         number_chapter = book_reader.reading(chapters, number_chapter)
#         book_reader.block_original.append(book_reader.data) # bd
#         summary = LLaMA.llama(book_reader.data, "sum", 0, 0, 0)
#         summary_edit = LLaMA.llama(summary, "edit", 0, 0, 0)
#         print(summary_edit + "\n")
#         input("")
#         if need_questions is True:
#             questions.create_questions(summary_edit, answer, book_reader)
#         SummaryBook.write(summary_edit)
#         SummaryBook.write("\n")
#         book_reader.data = ""
#     questions.right_answer = answer.right_answer
#     SummaryBook.close()


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
def process_chunk(book_reader,  mode, database, id_book):
    if database.collection_book.find_one({"_id": id_book})['stop_process'] == 0:
        number_block = 3
    else:
        number_block = database.collection_book.find_one({"_id": id_book})['stop_process']
    while True:
        if book_reader.flag_break is True:
            break
        if number_block < len(database.collection_book.find_one({'_id': id_book})['id_text']):
            book_reader.count_ready_block = database.collection_book.find_one({"_id": id_book})['count_ready_block']
            while book_reader.count_ready_block == 3:
                if book_reader.flag_break is True:
                    break
                time.sleep(1)  # Ожидание если достигнут лимит готовых блоков
            id_block = database.collection_book.find_one({'_id': id_book})['id_text'][number_block]
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
            database.collection_book.update_one({"_id": id_book}, {"$inc": {"count_ready_block": 1}})
            number_block += 1
            database.collection_book.update_one({"_id": id_book}, {"$set": {"stop_process": number_block}})
            book_reader.data = ""
        else:
            break


def get_text(database, book_reader, mode, id_book):
    id_text = database.collection_book.find_one({"_id": id_book})['id_text']
    book_reader.count_block = database.collection_book.find_one({"_id": id_book})['block_stop_book']
    id_block = id_text[book_reader.count_block]
    if book_reader.count_block < 3:
        text = database.collection_text.find_one({"_id": id_block})['original']
    # print(f"\n{arr_block[book_reader.count_block]}")
    else:
        if mode == "sum":
            text = database.collection_text.find_one({"_id": id_block})['sum']
        if mode == "time":
            text = database.collection_text.find_one({"_id": id_block})['sum_time']
    return text, id_block


# Главная асинхронная функция для управления процессом чтения и суммаризации
def process_text(name_file, book_reader, mode, database, id_book):
    #book_reader.flag_break = False
    file_path = f"uploads/{name_file}"
    if database.collection_book.find_one({'_id': id_book})['status'] == 'start':

        chapters = Divide.split_book_by_chapters(file_path)
        text = Divide.split_chapters(chapters, book_reader, database, id_book)
        database.collection_book.update_one({"_id": id_book}, {"$set": {'status': "reading"}})
    length_book = len_book(file_path)  # Получение длины книги

    book_reader.count_block = database.collection_book.find_one({"_id": id_book})['block_stop_book']
    if book_reader.count_block >= len(database.collection_book.find_one(
            {'_id': id_book})['id_text']):
        #
        return "end_file", 0, 0
    flag = 1
    count_ready_block = database.collection_book.find_one({"_id": id_book})['count_ready_block']
    # Основной цикл обработки и взаимодействия с пользователем
    if book_reader.count_block < len(database.collection_book.find_one({'_id': id_book})['id_text']):

        if count_ready_block >= 1:
            flag = 1
            start = time.time()
            text, id_block_current = get_text(database, book_reader, mode, id_book)
            # if need_questions is True:
            #     questions.create_questions(text, answer_user, book_reader, database, id_block)  # bd
            database.collection_book.update_one({"_id": id_book}, {"$inc": {"count_ready_block": -1}})
            id_text = database.collection_book.find_one({"_id": id_book})['id_text']
            # answer = ''
            # answer = input("Press Enter to continue, type 'original', 'exit', 'edit' for further processing...")
            # count_iter = 0
            # if answer == "exit":
            #     print("Ending the process =)...\n")
            #     book_reader.flag_break = True
            #     break
            # if answer == "original":
            #     print(book_reader.block_original[book_reader.count_block]) #bd
            # while answer == "edit":
            #     if count_iter == 4:
            #         print(book_reader.block_original[book_reader.count_block]) #bd
            #         break
            #     print("Please wait...\n")
            #     result = LLaMA.llama(book_reader.block_original[book_reader.count_block], "sum at time", count_sentences(book_reader.block_original[book_reader.count_block]) * book_reader.symbols_koef, 0, 0) # bd
            #     print(result)
            #     answer = input("Press Enter to continue or 'edit' for further processing...")
            end = time.time()
            reading_time = (end - start) / 60
            if mode == "sum":
                database.add_block_stop(book_reader.count_block, id_book)  # запомним фрагмент на котором остановился читатель
                database.add_chapter_stop(book_reader.number_chapter, id_book)
                return text, id_block_current, 0
            # if reading_time > 30:
            #     reading_time = 15
            # book_reader.reading_times.append(reading_time)  # bd
            # length_blocks = 0
            # time_blocks = 0
            # if book_reader.count_block >= 3:
            #     for i in range(1, 4):
            #         id_block = id_text[book_reader.count_block - i]
            #         if book_reader.count_block in [3, 4, 5]:
            #             text_time = database.collection_text.find_one({"_id": id_block})['original']
            #         else:
            #             if mode == "sum":
            #                 text_time = database.collection_text.find_one({"_id": id_block})['sum']
            #             if mode == "time":
            #                 text_time = database.collection_text.find_one({"_id": id_block})['sum_time']
            #         length_blocks += len(text_time)
            #         time_blocks += book_reader.reading_times[book_reader.count_block - i]
            #     speed_reading = length_blocks / time_blocks
            #     time_orig = length_book / speed_reading
            #     if time_orig <= time_full:
            #         book_reader.symbols_koef = 1
            #     else:
            #         book_reader.symbols_koef = time_full / time_orig
            #         database.add_block_stop(book_reader.count_block, id_book)  # запомним фрагмент на котором остановился читатель
            database.add_chapter_stop(book_reader.number_chapter, id_book)
            if mode == "time":
                return text, id_block_current, reading_time
        else:
            return "wait", 0, 0

    # database.add_block_stop(book_reader.count_block)  # запомним фрагмент на котором остановился читатель
    # database.add_chapter_stop(book_reader.number_chapter)
    # if mode == "time":
    #     print(f"Total reading time: {sum( book_reader.reading_times): .2f} minutes")


# def control(name_file, questions, answer, book_reader, database):
#     need_questions = input("Do you need questions? (yes/no): ")
#     while need_questions != "yes" and need_questions != "no":
#         need_questions = input("Do you need questions? (yes/no): ")
#     if need_questions == "yes":
#         need_questions = True
#     else:
#         need_questions = False
#     mode = input("Read in time or randomly summarized text(time/sum): ")
#     while mode != "time" and mode != "sum":
#         mode = input("Read in time or randomly summarized text(time/sum): ")
#     if mode == "time":
#         asyncio.run(process_text(name_file, need_questions, questions, answer, book_reader, "time", database))
#     if mode == "sum":
#         asyncio.run(process_text(name_file, need_questions, questions, answer, book_reader, "sum", database))
