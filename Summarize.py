import LLaMA
import BookReader
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
        book_reader.block_original.append(book_reader.data)
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
async def process_chunk(book_reader, arr_block, process_queue, chapters):
    while True:
        await process_queue.get()
        if book_reader.flag_break is True:
            break
        if book_reader.number_chapter < len(chapters):
            while book_reader.count_ready_block == 5:
                await asyncio.sleep(1)  # Ожидание если достигнут лимит готовых блоков
            book_reader.number_chapter = book_reader.reading(chapters, book_reader.number_chapter)
            length = count_sentences(book_reader.data)
            book_reader.block_original.append(book_reader.data)
            summary = LLaMA.llama(book_reader.data, "sum at time", book_reader.symbols_koef * length, 0, 0)
            summary_edit = LLaMA.llama(summary, "edit", 0, 0, 0)
            arr_block.append(summary_edit)
            book_reader.count_ready_block += 1
            book_reader.data = ""
            process_queue.task_done()
        else:
            break


# Главная асинхронная функция для управления процессом чтения и суммаризации
async def main(name_file, need_questions, questions, answer_user, book_reader):
    length_book = len_book(name_file)  # Получение длины книги
    days = int(input("Enter the number of days: "))
    hours = float(input("Enter the number of hours per day: "))
    time_full = days * hours * 60  # Полное время для чтения (в минутах)
    chapters = Divide.split_book_by_chapters(name_file)  # Разделение книги на главы
    arr_block = []
    process_queue = asyncio.Queue()
    task_chunk = asyncio.create_task(process_chunk(book_reader, arr_block, process_queue, chapters))

    # Начальная обработка первых трех глав
    for _ in range(3):
        if book_reader.number_chapter < len(chapters):
            book_reader.number_chapter = book_reader.reading(chapters, book_reader.number_chapter)
            arr_block.append(book_reader.data)
            book_reader.block_original.append(book_reader.data)
            book_reader.count_ready_block += 1
        book_reader.data = ""

    # Подача задач в очередь на обработку
    for _ in range(3):
        await process_queue.put(None)
    reading_times = []
    flag = 1
    # Основной цикл обработки и взаимодействия с пользователем
    while book_reader.number_chapter < len(chapters):
        if len(chapters[book_reader.number_chapter]) < 200:
            book_reader.number_chapter += 1
            continue
        length_blocks = 0
        time_blocks = 0
        await process_queue.put(None)
        if book_reader.count_ready_block >= 1:
            flag = 1
            start = time.time()
            print(f"\n{arr_block[book_reader.count_block]}")
            if need_questions is True:
                questions.create_questions(arr_block[book_reader.count_block], answer_user, book_reader)
            book_reader.count_ready_block -= 1
            answer = input("Press Enter to continue, type 'original', 'exit', 'edit' for further processing...")
            count_iter = 0
            if answer == "exit":
                print("Ending the process =)...\n")
                book_reader.flag_break = True
                break
            if answer == "original":
                print(book_reader.block_original[book_reader.count_block])
            while answer == "edit":
                if count_iter == 4:
                    print(book_reader.block_original[book_reader.count_block])
                    break
                print("Please wait...\n")
                result = LLaMA.llama(book_reader.block_original[book_reader.count_block], "sum at time", count_sentences(book_reader.block_original[book_reader.count_block]) * book_reader.symbols_koef)
                print(result)
                answer = input("Press Enter to continue or 'edit' for further processing...")
            end = time.time()
            reading_time = (end - start) / 60
            if reading_time > 30:
                reading_time = 15
            reading_times.append(reading_time)
            if book_reader.count_block >= 3:
                for i in range(1, 4):
                    length_blocks += len(arr_block[book_reader.count_block - i])
                    time_blocks += reading_times[book_reader.count_block - i]
                speed_reading = length_blocks / time_blocks
                time_orig = length_book / speed_reading
                if time_orig <= time_full:
                    print("You will read the book in the original in this time and at this reading speed")
                    book_reader.symbols_koef = 1
                else:
                    book_reader.symbols_koef = time_full / time_orig

            print(f"Reading time of fragment {book_reader.count_block + 1}: {reading_time:.2f} minutes\n")
            print(f'Compression coefficient - {book_reader.symbols_koef}\n')
            book_reader.count_block += 1
        else:
            if flag == 1:
                print("Please wait, the fragment is not processed yet.")
            flag = 0
            await asyncio.sleep(1)
    questions.right_answer = answer_user.right_answer
    print(f"Total reading time: {sum(reading_times): .2f} minutes")


def control(name_file, questions, answer, book_reader):
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
        asyncio.run(main(name_file, need_questions, questions, answer, book_reader))
    if mode == "sum":
        summarize(name_file, name_sum_file, need_questions, questions, answer, book_reader)
