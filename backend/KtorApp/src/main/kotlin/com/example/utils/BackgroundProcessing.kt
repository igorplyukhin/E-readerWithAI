package com.example.utils

import com.example.models.*
import org.bson.Document
import org.bson.types.ObjectId
import kotlinx.coroutines.*
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates

object BackgroundProcessing {

    /**
     * Фоновая обработка загруженной книги.
     * @param idUser ID пользователя, загрузившего книгу.
     * @param filePath Путь к файлу книги на сервере.
     */
    /**
     * Фоновая обработка загруженной книги.
     * @param idUser ID пользователя, загрузившего книгу.
     * @param filePath Путь к файлу книги на сервере.
     * @param nameFile Название файла книги.
     */
    suspend fun processBookInBackground(idUser: String, filePath: String, nameFile: String) {
        withContext(Dispatchers.IO) {
            // Инициализация объектов для работы с книгой
            val bookProcessor = BookProcessor(filePath, nameFile)
            val chapters = bookProcessor.getChapters()
            var book = bookProcessor.getBook()

            // Создание записи о книге в базе данных
            val booksCollection = DatabaseFactory.getBooksCollection()
            booksCollection.insertOne(book.toDocument())

            val bookId = book.idBook

            // Обновление массива bookIds у пользователя
            val usersCollection = DatabaseFactory.getUsersCollection()
            usersCollection.updateOne(
                Filters.eq("_id", idUser),
                Updates.addToSet("bookIds", bookId)
            )

            // Разделение книги на главы и блоки
            val textBlocks = mutableListOf<Document>()
            for ((chapterIndex, chapter) in chapters.withIndex()) {
                val blocks = bookProcessor.divideChapterIntoBlocks(chapter)
                for (block in blocks) {
                    val idBlock = ObjectId().toString()
                    val textBlock = TextBlock(
                        idBlock = idBlock,
                        original = block,
                        numberChapter = chapterIndex + 1
                    )
                    textBlocks.add(textBlock.toDocument())

                    // Связывание блоков с книгой
                    booksCollection.updateOne(
                        Filters.eq("_id", bookId),
                        Updates.push("textBlockIds", idBlock)
                    )
                }
            }

            // Вставка текстовых блоков в базу данных
            val textBlocksCollection = DatabaseFactory.getTextBlocksCollection()
            if (textBlocks.isNotEmpty()) {
                textBlocksCollection.insertMany(textBlocks)
            }

            // Обновление статуса книги на "ready"
            booksCollection.updateOne(
                Filters.eq("_id", bookId),
                Updates.set("status", "ready")
            )
        }
    }

    /**
     * Фоновая обработка суммирования для отдельного текстового блока.
     * @param textBlock Текстовый блок для обработки.
     * @param mode Режим суммирования ("summarization" или "summarization_time").
     */
    suspend fun processSummarizationForBlock(textBlock: TextBlock, mode: String) {
        withContext(Dispatchers.IO) {
            val textBlocksCollection = DatabaseFactory.getTextBlocksCollection()
            val summarizedText = when (mode) {
                "summarization" -> summarizeText(textBlock.original)
                "summarization_time" -> summarizeTextWithTime(textBlock.original)
                else -> textBlock.original
            }

            val updateField = if (mode == "summarization") "summary" else "summaryTime"
            textBlocksCollection.updateOne(
                Filters.eq("_id", textBlock.idBlock),
                Updates.set(updateField, summarizedText)
            )
        }
    }

    /**
     * Фоновая обработка для режима суммирования.
     * @param book Книга, для которой выполняется суммирование.
     * @param mode Режим суммирования ("summarization" или "summarization_time").
     */
    suspend fun processSummarizationMode(book: Book, mode: String) {
        withContext(Dispatchers.IO) {
            val textBlocksCollection = DatabaseFactory.getTextBlocksCollection()

            // Получаем все текстовые блоки книги
            val blocksCursor = textBlocksCollection.find(Filters.`in`("_id", book.textBlockIds))
            val blocks = blocksCursor.map { it.toTextBlock() }.toList()

            // Обработка каждого блока
            for (block in blocks) {
                val summarizedText = when (mode) {
                    "summarization" -> summarizeText(block.original)
                    "summarization_time" -> summarizeTextWithTime(block.original)
                    else -> block.original
                }

                // Обновляем текстовый блок в базе данных
                val updateField = if (mode == "summarization") "summary" else "summaryTime"
                textBlocksCollection.updateOne(
                    Filters.eq("_id", block.idBlock),
                    Updates.set(updateField, summarizedText)
                )
            }

            // Обновление статуса книги
            val booksCollection = DatabaseFactory.getBooksCollection()
            booksCollection.updateOne(
                Filters.eq("_id", book.idBook),
                Updates.set("status", "summarized")
            )
        }
    }

    /**
     * Функция для суммирования текста.
     * @param text Оригинальный текст.
     * @return Суммированный текст.
     */
    fun summarizeText(text: String): String {
        // Реализуйте алгоритм суммирования текста
        // Здесь можно использовать библиотеку NLP или API
        return "Суммированный текст"
    }

    /**
     * Функция для суммирования текста с учетом времени чтения.
     * @param text Оригинальный текст.
     * @return Суммированный текст, оптимизированный по времени чтения.
     */
    fun summarizeTextWithTime(text: String): String {
        // Реализуйте алгоритм суммирования с учетом времени чтения
        return "Суммированный текст с учетом времени"
    }

    /**
     * Генерация вопросов и ответов по текстовому блоку.
     * @param text Текстовый блок.
     * @return Пара списков вопросов и ответов.
     */
    fun generateQuestionsForBlock(text: String): Pair<List<String>, List<String>> {
        // Реализуйте генерацию вопросов и ответов по тексту
        val questions = listOf("Вопрос 1 по блоку", "Вопрос 2 по блоку")
        val answers = listOf("Ответ 1", "Ответ 2")
        return Pair(questions, answers)
    }

    /**
     * Генерация теста по всей книге.
     * @param idBook ID книги.
     * @return Карта с вопросами и ответами.
     */
    suspend fun generateTestForBook(idBook: String): Map<String, Any> {
        val textBlocksCollection = DatabaseFactory.getTextBlocksCollection()

        // Получаем все текстовые блоки книги
        val blocksCursor = textBlocksCollection.find(Filters.eq("bookId", idBook))
        val blocks = blocksCursor.map { it.toTextBlock() }.toList()

        val questions = mutableListOf<String>()
        val answers = mutableListOf<String>()

        for (block in blocks) {
            val (blockQuestions, blockAnswers) = generateQuestionsForBlock(block.original)
            questions.addAll(blockQuestions)
            answers.addAll(blockAnswers)

            // Обновляем текстовый блок в базе данных
            textBlocksCollection.updateOne(
                Filters.eq("_id", block.idBlock),
                Updates.combine(
                    Updates.set("questions", blockQuestions),
                    Updates.set("rightAnswers", blockAnswers)
                )
            )
        }

        return mapOf("questions" to questions, "answers" to answers)
    }

    /**
     * Получение пересказа книги.
     * @param idBook ID книги.
     * @return Пересказ книги.
     */
    suspend fun getBookRetelling(idBook: String): String {
        val textBlocksCollection = DatabaseFactory.getTextBlocksCollection()

        // Получаем суммированные тексты всех блоков
        val blocksCursor = textBlocksCollection.find(Filters.eq("bookId", idBook))
        val summaries = blocksCursor.mapNotNull { it.getString("summary") }.toList()

        // Объединяем суммированные тексты в один пересказ
        return summaries.joinToString("\n")
    }

    /**
     * Получение рекомендаций похожих книг.
     * @param idBook ID книги.
     * @return Список рекомендованных книг.
     */
    suspend fun getSimilarBooks(idBook: String): List<Book> {
        // Реализуйте логику рекомендаций на основе жанра, автора или других параметров
        val booksCollection = DatabaseFactory.getBooksCollection()

        // Для примера выбираем случайные книги
        val randomBooksCursor = booksCollection.find().limit(5)
        return randomBooksCursor.map { it.toBook() }.toList()
    }
}
