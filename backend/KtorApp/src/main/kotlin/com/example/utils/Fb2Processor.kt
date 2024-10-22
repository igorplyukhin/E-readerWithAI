package com.example.utils

import com.example.models.BookText
import com.example.models.FictionBook
import org.simpleframework.xml.core.Persister
import java.io.File

class Fb2Processor(private val filePath: String) {

    /**
     * Метод для извлечения текста из FB2 файла.
     * Использует Simple XML для десериализации файла в объект FictionBook.
     *
     * @return объект BookText с заголовком, авторами, содержимым и аннотацией книги
     */
    fun extractBookText(): BookText {
        val file = File(filePath)
        val serializer = Persister()

        // Парсим FB2 файл в объект FictionBook
        val book: FictionBook = try {
            serializer.read(FictionBook::class.java, file)
        } catch (e: Exception) {
            throw Exception("Ошибка при парсинге FB2 файла: ${e.message}")
        }

        // Извлекаем заголовок
        val title = book.description?.titleInfo?.bookTitle ?: "Название не найдено"

        // Извлекаем авторов
        val authors = book.description?.titleInfo?.authors
            ?.joinToString(separator = ", ") { "${it.firstName ?: ""} ${it.lastName ?: ""}".trim() }
            ?.takeIf { it.isNotBlank() }
            ?: "Автор не указан"

        // Извлекаем аннотацию
        val annotation = book.description?.titleInfo?.annotation?.paragraphs
            ?.joinToString("\n") { it.trim() }
            ?.takeIf { it.isNotBlank() }
            ?: "Аннотация отсутствует"

        // Извлекаем содержимое книги
        val contentBuilder = StringBuilder()

        // Обработка заголовков из <body>
        book.body?.titles?.forEach { titleObj ->
            titleObj.paragraphs?.forEach { p ->
                contentBuilder.append(p.trim()).append("\n\n")
            }
        }

        // Обработка секций
        book.body?.sections?.forEach { section ->
            contentBuilder.append(extractAllTextFromSection(section))
            contentBuilder.append("\n\n")
        }

        val content = if (contentBuilder.isEmpty()) "Содержание отсутствует" else contentBuilder.toString().trim()

        return BookText(title, authors, content, annotation)
    }

    /**
     * Рекурсивный метод для извлечения текста из секции и всех вложенных секций.
     */
    private fun extractAllTextFromSection(section: com.example.models.Section): String {
        val titlesText = section.titles?.joinToString("\n") {
            it.paragraphs?.joinToString("\n") { it.trim() } ?: ""
        } ?: ""
        val paragraphs = section.paragraphs?.joinToString("\n") { it.trim() } ?: ""

        val nestedSections = section.sections?.joinToString("\n\n") { nestedSection ->
            extractAllTextFromSection(nestedSection)
        } ?: ""

        return listOfNotNull(
            if (titlesText.isNotEmpty()) "### $titlesText ###" else null,
            if (paragraphs.isNotEmpty()) paragraphs else null,
            if (nestedSections.isNotEmpty()) nestedSections else null
        ).joinToString("\n\n")
    }
}
