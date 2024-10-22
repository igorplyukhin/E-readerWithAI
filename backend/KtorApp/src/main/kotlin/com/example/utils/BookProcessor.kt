package com.example.utils

import com.example.models.Book
import com.example.models.BookText
import com.example.models.TextBlock
import org.apache.pdfbox.pdmodel.PDDocument
import org.apache.pdfbox.text.PDFTextStripper
import org.bson.types.ObjectId
import java.io.File

class BookProcessor(private val filePath: String, private val nameFile: String) {

    /**
     * Чтение текстового файла.
     */
    fun readTextFile(): String {
        return File(filePath).readText()
    }

    /**
     * Чтение PDF-файла и извлечение текста.
     */
    fun readPdfFile(): String {
        PDDocument.load(File(filePath)).use { document ->
            val pdfStripper = PDFTextStripper()
            return pdfStripper.getText(document) // Используем метод getText(document)
        }
    }

    /**
     * Чтение FB2-файла и извлечение структурированных данных.
     */
    fun readFb2File(): BookText {
        val fb2Processor = Fb2Processor(filePath)
        return fb2Processor.extractBookText()
    }

    /**
     * Получение списка глав из содержимого книги.
     */
    fun getChapters(fileType: String): List<String> {
        val content = when (fileType) {
            "text/plain" -> readTextFile()
            "application/pdf" -> readPdfFile()
            "application/fb2+xml" -> readFb2File().content
            else -> throw IllegalArgumentException("Unsupported file type")
        }
        return content.split(Regex("(Глава|Часть)\\s+\\d+", RegexOption.IGNORE_CASE))
            .filter { it.isNotBlank() }
    }

    /**
     * Создание объекта Book на основе типа файла.
     */
    fun getBook(fileType: String): Book {
        val bookText = when (fileType) {
            "text/plain" -> {
                val content = readTextFile()
                BookText(
                    title = extractLineContent(content, "Title:") ?: "Название не указано",
                    authors = extractLineContent(content, "Author(s):") ?: "Автор книги не указан",
                    content = extractLineContent(content, "Content:") ?: "Описание отсутствует",
                    annotation = null // Текстовые файлы, возможно, не содержат аннотацию
                )
            }
            "application/pdf" -> {
                val text = readPdfFile()
                // Предполагается, что PDF обрабатывается аналогично FB2
                BookText(
                    title = "Неизвестно", // PDF-парсер не извлекает метаданные
                    authors = "Неизвестно",
                    content = text,
                    annotation = null // PDF-файлы, возможно, не содержат аннотацию
                )
            }
            "application/fb2+xml" -> readFb2File()
            else -> throw IllegalArgumentException("Unsupported file type")
        }

        val idBook = ObjectId().toString()

        return Book(
            idBook = idBook, // Здесь idBook создается
            title = bookText.title,
            author = bookText.authors,
            description = bookText.content,
            annotation = bookText.annotation,
            status = "reading",
            mode = "default",
            nameFile = nameFile,
            filePath = filePath
        )
    }

    /**
     * Вспомогательный метод для извлечения содержимого после заданного префикса.
     */
    private fun extractLineContent(content: String, prefix: String): String? {
        val regex = Regex("(?i)$prefix\\s*(.*)")
        val matchResult = regex.find(content)
        return matchResult?.groups?.get(1)?.value?.trim()
    }

    /**
     * Разделение главы на блоки по 1000 символов.
     */
    fun divideChapterIntoBlocks(chapter: String): List<String> {
        val blockSize = 1000
        val blocks = mutableListOf<String>()
        var startIndex = 0

        while (startIndex < chapter.length) {
            val endIndex = (startIndex + blockSize).coerceAtMost(chapter.length)
            blocks.add(chapter.substring(startIndex, endIndex))
            startIndex = endIndex
        }

        return blocks
    }

    /**
     * Обработка глав и разделение их на текстовые блоки.
     */
    fun processChaptersAndBlocks(chapters: List<String>): List<TextBlock> {
        val textBlocks = mutableListOf<TextBlock>()
        chapters.forEachIndexed { chapterIndex, chapterContent ->
            val blocks = divideChapterIntoBlocks(chapterContent)
            blocks.forEach { blockContent ->
                val textBlock = TextBlock(
                    _id = ObjectId().toString(), // Используем _id вместо idBlock
                    original = blockContent,
                    numberChapter = chapterIndex + 1
                )
                textBlocks.add(textBlock)
            }
        }
        return textBlocks
    }
}
