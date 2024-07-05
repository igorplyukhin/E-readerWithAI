class BookReader:
    def __init__(self, name_file, count_answer=4, step_read=1, data='', count_symbols=0, end_file=True, block_text=3000):
        self.name_file = name_file
        self.count_answer = count_answer
        self.step_read = step_read
        self.data = data
        self.count_symbols = count_symbols
        self.end_file = end_file
        self.block_text = block_text
    def read_block(self,book):
        while self.count_symbols < self.block_text:
            char = book.read(self.step_read)
            if char == '':
                self.end_file = False
                break
            self.data += char
            if char != ' ':
                self.count_symbols += self.step_read
    def read_until_paragraph(self,book):
        while True:
            char = book.read(self.step_read)
            if char == '':
                self.end_file = False
                break
            self.data += char
            if char == '\n':
                self.count_symbols = 0
                break