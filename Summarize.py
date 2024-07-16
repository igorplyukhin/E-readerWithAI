import LLaMA
import BookReader
import Divide
import asyncio
import time


# Функция для суммаризации книги и записи результатов в файл
def summarize(name_file, name_sum_file):
    print("Обрабатываем ваш текст =)...")
    book_reader = BookReader.BookReader(name_file)
    encoding = book_reader.detect_encoding()
    chapters = Divide.split_book_by_chapters(name_file)
    SummaryBook = open(name_sum_file, "w", encoding=encoding)
    number_chapter = 0
    while number_chapter < len(chapters):
        if len(chapters[number_chapter]) < 200:
            number_chapter += 1
            continue
        number_chapter = book_reader.reading(chapters, number_chapter)
        summary = LLaMA.llama(book_reader.data, "sum", 0, 0, 0)
        summary_edit = LLaMA.llama(summary, "edit", 0, 0, 0)
        SummaryBook.write(summary_edit)
        SummaryBook.write("\n")
        book_reader.data = ""
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
async def process_chunk(book_reader, arr_block, process_queue, chapters, block_original):
    while True:
        await process_queue.get()

        if book_reader.number_chapter < len(chapters):
            while book_reader.count_ready_block == 5:
                await asyncio.sleep(1)  # Ожидание если достигнут лимит готовых блоков
            book_reader.number_chapter = book_reader.reading(chapters, book_reader.number_chapter)
            length = count_sentences(book_reader.data)
            block_original.append(book_reader.data)
            summary = LLaMA.llama(book_reader.data, "sum at time", book_reader.symbols_koef * length, 0, 0)
            summary_edit = LLaMA.llama(summary, "edit", 0, 0, 0)
            arr_block.append(summary_edit)
            book_reader.count_ready_block += 1
            book_reader.data = ""
            process_queue.task_done()
        else:
            break


# Главная асинхронная функция для управления процессом чтения и суммаризации
async def main(name_file):
    length_book = len_book(name_file)  # Получение длины книги

    time_full = 10 * 2 * 60  # Полное время для чтения (в минутах)
    chapters = Divide.split_book_by_chapters(name_file)  # Разделение книги на главы
    book_reader = BookReader.BookReader(chapters)
    block_original = []
    arr_block = []
    process_queue = asyncio.Queue()
    task_chunk = asyncio.create_task(process_chunk(book_reader, arr_block, process_queue, chapters, block_original))

    # Начальная обработка первых трех глав
    for _ in range(3):
        if book_reader.number_chapter < len(chapters):
            book_reader.number_chapter = book_reader.reading(chapters, book_reader.number_chapter)
            arr_block.append(book_reader.data)
            block_original.append(book_reader.data)
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
            print(f"Фрагмент {book_reader.count_block + 1}:\n{arr_block[book_reader.count_block]}")
            book_reader.count_ready_block -= 1
            answer = input("Нажмите Enter, чтобы продолжить, original, edit для обработки фрагмента ещё раз...")
            count_iter = 0
            if answer == "original":
                print(block_original[book_reader.count_block])
            while answer == "edit":
                if count_iter == 4:
                    print(block_original[book_reader.count_block])
                    break
                print("Подождите...\n")
                result = LLaMA.llama(block_original[book_reader.count_block], "sum at time", count_sentences(block_original[book_reader.count_block]) * book_reader.symbols_koef)
                print(result)
                answer = input("Нажмите Enter, чтобы продолжить или edit для обработки фрагмента ещё раз...")
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
                    print("Вы прочтёте книгу в оригинале за это время и с такой скоростью чтения")
                    book_reader.symbols_koef = 1
                else:
                    book_reader.symbols_koef = time_full / time_orig

            print(f"Время чтения фрагмента {book_reader.count_block + 1}: {reading_time:.2f} минуты\n")
            print(f'Коэфициент сжатия - {book_reader.symbols_koef}\n')
            book_reader.count_block += 1
        else:
            if flag == 1:
                print("Подождите, фрагмент еще не обработан.")
            flag = 0
            await asyncio.sleep(1)

    print(f"Общее время чтения: {sum(reading_times): .2f} минут")


def control(name_file):
    name_sum_file = "SummaryBook.txt"
    mode = input("time/sum: ")
    if mode == "time":
        asyncio.run(main(name_file))
    if mode == "sum":
        summarize(name_file, name_sum_file)
