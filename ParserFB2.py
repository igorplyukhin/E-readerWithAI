import xml.etree.ElementTree as ET
import os


class FB2Parser:
    def __init__(self, filename, external_annotations=True):
        self.root = ET.parse(filename).getroot()
        self.cleanup()
        self.external_annotations = external_annotations

    def cleanup(self):
        for element in self.root.iter():
                element.tag = element.tag.partition('}')[-1]

    def is_flat(self):
        return self.root.find('./body/section/section') is None

    def extract(self):
        self._book_title = self.root.find('./description/title-info/book-title').text
        self._main, *rest, self._annotations = self.root.findall('body')
        if self.is_flat():
            self.write(self.split(self._main))
        else:
            for part_id, part in enumerate(self._main.findall('section')):
                self.write(self.split(part, id=part_id))
        self.write_description()
        if self._annotations and self.external_annotations:
            self.write_annotations()

    def split(self, section, id=None):
        part_title = section.find('./title/p').text
        parts = {}
        for chapter_id, chapter in enumerate(section.findall('section')):
            chapter_title = chapter.find('./title/p').text
            part_path = '%02d_%s' % (id, part_title) if id is not None else ''
            chapter_path = os.path.join(part_path,
                                        '%02d_%s.fb2' % (chapter_id, chapter_title))
            path = os.path.join('.', self._book_title, chapter_path)
            parts[path] = chapter
        return parts

    def write_description(self):
        path = os.path.join('.', self._book_title, 'description.fb2')
        fb = ET.Element('FictionBook', attrib={'xmlns': "http://www.gribuser.ru/xml/fictionbook/2.0"})
        fb.append(self.root.find('description'))
        images = self.root.find('binary')
        if images:
            fb.append(images)
        book = ET.ElementTree(fb)
        book.write(path, encoding='utf-8', xml_declaration=True)

    def write_annotations(self):
        path = os.path.join('.', self._book_title, 'annotations.fb2')
        self.write({path: self._annotations})

    def write(self, data):
        for path, chapter in data.items():
            dir = os.path.dirname(path)
            fb = ET.Element('FictionBook',
                            attrib={'xmlns': "http://www.gribuser.ru/xml/fictionbook/2.0"})
            body = ET.SubElement(fb, 'body')
            body.append(chapter)
            if self._annotations and not self.external_annotations:
                body.append(self._annotations)
            book = ET.ElementTree(fb)
            os.makedirs(dir, exist_ok=True)
            book.write(path, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    FB2Parser('gmn.fb2').extract()

class BookReader:
    def __init__(self, name_file, count_answer=4, step_read=1, block_text=300):
        self.name_file = name_file
        self.count_answer = count_answer
        self.step_read = step_read
        self.block_text = block_text
        self.data = ''
        self.count_symbols = 0
        self.end_file = True

    def read_and_process(self):
        with open(self.name_file, 'r', encoding='utf-8') as f:
            while self.end_file:
                self.read_block(f)
                if self.count_symbols == self.block_text:
                    self.read_until_period(f)
                self.prompt_user()
                print(self.data)
                self.data = ""

    def read_block(self, f):
        while self.count_symbols < self.block_text:
            char = f.read(self.step_read)
            if char == '':
                self.end_file = False
                break
            self.data += char
            if char != ' ':
                self.count_symbols += self.step_read

    def read_until_period(self, f):
        while True:
            char = f.read(self.step_read)
            if char == '':
                self.end_file = False
                break
            self.data += char
            if char == '.':
                self.count_symbols = 0
                break

    def prompt_user(self):
        answer_user = input("Введите номер ответа (1-4): ")
        while not answer_user.isdigit() or int(answer_user) > self.count_answer or int(answer_user) < 1:
            if answer_user.isdigit() == 1:
                print(f"Выберете варианты ответа 1 - {self.count_answer}!")
            else:
                print("Введите число!")
            answer_user = input("Введите номер ответа (1-4): ")

# Использование класса BookReader
name_file = "book.txt"
book_reader = BookReader(name_file)
book_reader.read_and_process()
