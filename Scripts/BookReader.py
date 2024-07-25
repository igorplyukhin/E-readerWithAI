import chardet


class BookReader:

    def __init__(self,name_file, count_answer=4, step_read=1, data='', count_symbols=0, end_file=True, block_text=3000):
        self.count_answer = count_answer
        self.step_read = step_read
        self.data = data
        self.count_symbols = count_symbols
        self.end_file = end_file
        self.block_text = block_text
        self.number_chapter = 0
        self.count_block = 0
        self.count_ready_block = 0
        self.symbols_koef = 1
        self.block_original = []
        self.flag_break = False
        self.reading_times = []
        self.name_file = name_file


    def detect_encoding(self):
        with open(self.name_file, 'rb') as file:
            raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']

    def reading(self, chapters, number_chapter):
        length = len(chapters[number_chapter])
        count_symbols_str = self.read_block(chapters[number_chapter])
        if self.count_symbols == self.block_text:
            count_symbols_str = self.read_until_paragraph(chapters[number_chapter], count_symbols_str)
        if count_symbols_str >= length - 1:
            number_chapter += 1  # Переходим к следующей главе
        else:
            chapters[number_chapter] = chapters[number_chapter][count_symbols_str:]
        return number_chapter

    def read_block(self, chapter):
        self.count_symbols = 0
        block_text = self.block_text
        if len(chapter) < self.block_text:
            block_text = len(chapter)
        while self.count_symbols < block_text:
            char = chapter[self.count_symbols]
            if char == '':
                self.end_file = False
                break
            self.data += char
            self.count_symbols += self.step_read
        return self.count_symbols

    def read_until_paragraph(self, chapter, symbols):
        while True:
            if symbols > len(chapter)-1:
                self.count_symbols = 0
                break
            char = chapter[symbols]
            if char == '':
                self.end_file = False
                break
            self.data += char
            if char == '\n':
                self.count_symbols = 0
                break
            symbols += 1
        return symbols