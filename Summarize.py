import BookReader
import LLaMA
def summarize(name_file, name_sum_file):
    print("Обрабатываем ваш текст =)...")
    book_reader = BookReader.BookReader(name_file)
    SummaryBook = open(name_sum_file, "w", encoding="utf-8")
    with open(book_reader.name_file, 'r', encoding='utf-8') as book:
        while book_reader.end_file:
            book_reader.read_block(book)
            if book_reader.count_symbols == book_reader.block_text:
                book_reader.read_until_paragraph(book)
            summary = LLaMA.llama(book_reader.data, "sum", 0)
            #Обработка
            SummaryBook.write(summary)
            SummaryBook.write("\n")
    SummaryBook.close()
    book.close()
