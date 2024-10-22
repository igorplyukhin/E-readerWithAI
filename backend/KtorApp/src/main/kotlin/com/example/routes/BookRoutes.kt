package com.example.routes

import com.example.models.BookDetailResponse
import com.example.models.BookPageResponse
import com.example.models.BookResponse
import com.example.models.BookText
import io.ktor.server.routing.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.http.*
import com.example.utils.*
import com.example.utils.toBook
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import io.ktor.http.content.PartData
import io.ktor.http.content.forEachPart
import kotlinx.coroutines.*
import java.io.File
import io.ktor.utils.io.jvm.javaio.copyTo
import org.bson.Document
import org.bson.types.ObjectId

fun Route.bookRoutes() {
    post("/upload_book") {
        val multipart = call.receiveMultipart()
        var userId: String? = null
        var fileName: String? = null
        var fileType: String? = null
        var bookText: BookText? = null

        multipart.forEachPart { part ->
            when (part) {
                is PartData.FormItem -> {
                    if (part.name == "id") {
                        userId = part.value
                    }
                }
                is PartData.FileItem -> {
                    if (part.name == "file") {
                        fileName = part.originalFileName ?: "default.fb2"
                        fileType = getSupportedFileType(part, fileName)

                        if (fileType == null) {
                            call.respond(
                                HttpStatusCode.UnsupportedMediaType,
                                BookResponse(
                                    status = "error",
                                    message = "Неподдерживаемый тип файла"
                                )
                            )
                            return@forEachPart
                        }

                        val uploadDir = File("uploads")
                        if (!uploadDir.exists() && !uploadDir.mkdirs()) {
                            call.respond(
                                HttpStatusCode.InternalServerError,
                                BookResponse(
                                    status = "error",
                                    message = "Не удалось создать директорию для загрузки файлов"
                                )
                            )
                            return@forEachPart
                        }

                        val filePath = saveFile(part, uploadDir, fileName)
                        if (filePath == null) {
                            call.respond(
                                HttpStatusCode.InternalServerError,
                                BookResponse(
                                    status = "error",
                                    message = "Ошибка при сохранении файла"
                                )
                            )
                            return@forEachPart
                        }

                        bookText = when (fileType) {
                            "application/pdf" -> {
                                val bookProcessor = BookProcessor(filePath.path, fileName)
                                BookText(
                                    title = "Неизвестно", // Можно добавить извлечение из метаданных
                                    authors = "Неизвестно",
                                    content = bookProcessor.readPdfFile(),
                                    annotation = null // PDF-файлы могут не содержать аннотацию
                                )
                            }
                            "application/fb2+xml" -> {
                                val fb2Processor = Fb2Processor(filePath.path)
                                fb2Processor.extractBookText()
                            }
                            "text/plain" -> {
                                val content = BookProcessor(filePath.path, fileName).readTextFile()
                                BookText(
                                    title = "Неизвестно",
                                    authors = "Неизвестно",
                                    content = content,
                                    annotation = null // Текстовые файлы могут не содержать аннотацию
                                )
                            }
                            else -> null
                        }

                        if (bookText == null) {
                            call.respond(
                                HttpStatusCode.InternalServerError,
                                BookResponse(
                                    status = "error",
                                    message = "Ошибка при обработке файла"
                                )
                            )
                            return@forEachPart
                        }
                    }
                }
                else -> {
                    // Игнорируем другие типы частей
                }
            }
            part.dispose()
        }

        // Присваиваем bookText к локальной неизменяемой переменной после проверки на null
        val finalBookText = bookText
        val finalUserId = userId
        val finalFileName = fileName
        val finalFileType = fileType

        if (finalUserId == null || finalFileName == null || finalBookText == null) {
            call.respond(
                HttpStatusCode.BadRequest,
                BookResponse(
                    status = "error",
                    message = "Не предоставлен файл, ID пользователя или содержание книги"
                )
            )
            return@post
        }

        val bookProcessor = BookProcessor("uploads/$finalFileName", finalFileName)
        val book = bookProcessor.getBook(finalFileType ?: "text/plain")
        val chapters = bookProcessor.getChapters(finalFileType ?: "text/plain")

        val textBlocks = bookProcessor.processChaptersAndBlocks(chapters)

        // Обновление базы данных без транзакций
        val booksCollection = DatabaseFactory.getBooksCollection()
        val textBlocksCollection = DatabaseFactory.getTextBlocksCollection()
        val usersCollection = DatabaseFactory.getUsersCollection()

        try {
            booksCollection.insertOne(book.toDocument())

            val textBlocksDocuments = textBlocks.map { it.toDocument() }
            textBlocksCollection.insertMany(textBlocksDocuments)

            booksCollection.updateOne(
                Filters.eq("_id", ObjectId(book.idBook)),
                Updates.set("textBlockIds", textBlocks.map { it._id }) // Используем _id вместо idBlock
            )

            usersCollection.updateOne(
                Filters.eq("_id", finalUserId),
                Updates.combine(
                    Updates.addToSet("bookIds", book.idBook),
                    Updates.inc("countBook", 1)
                )
            )
        } catch (e: Exception) {
            call.respond(
                HttpStatusCode.InternalServerError,
                BookResponse(
                    status = "error",
                    message = "Ошибка при обновлении базы данных: ${e.message}"
                )
            )
            return@post
        }

        // Отправляем успешный ответ с объектом книги
        call.respond(
            HttpStatusCode.OK,
            BookResponse(
                status = "success",
                message = "Книга успешно загружена и обработана",
                book = book
            )
        )
    }


    // Маршрут для получения информации о книге
    post("/get_book") {
        val parameters = call.receiveParameters()
        val idBook = parameters["id_book"]

        if (idBook == null) {
            call.respond(
                HttpStatusCode.BadRequest,
                BookResponse(
                    status = "error",
                    message = "ID книги не предоставлен"
                )
            )
            return@post
        }

        val booksCollection = DatabaseFactory.getBooksCollection()
        val bookDoc = booksCollection.find(Filters.eq("_id", ObjectId(idBook))).firstOrNull()

        if (bookDoc != null) {
            val book = bookDoc.toBook()
            call.respond(
                HttpStatusCode.OK,
                book // Убедитесь, что Book аннотирован как @Serializable
            )
        } else {
            call.respond(
                HttpStatusCode.NotFound,
                BookResponse(
                    status = "error",
                    message = "Книга не найдена"
                )
            )
        }
    }

    // Маршрут для изменения режима работы с книгой
    post("/change_mode") {
        val parameters = call.receiveParameters()
        val idBook = parameters["id_book"]
        val mode = parameters["mode"]

        if (idBook == null || mode == null) {
            call.respond(HttpStatusCode.BadRequest, "Не предоставлены необходимые параметры")
            return@post
        }

        val booksCollection = DatabaseFactory.getBooksCollection()
        val bookDoc = booksCollection.find(Filters.eq("_id", ObjectId(idBook))).firstOrNull()

        if (bookDoc == null) {
            call.respond(HttpStatusCode.NotFound, "Книга не найдена")
            return@post
        }

        when (mode) {
            "summarization", "summarization_time" -> {
                // Запуск фоновой обработки для суммирования текста
                call.application.launch {
                    BackgroundProcessing.processSummarizationMode(bookDoc.toBook(), mode)
                }
                val updateResult = booksCollection.updateOne(
                    Filters.eq("_id", ObjectId(idBook)),
                    Updates.set("mode", mode)
                )
                if (updateResult.matchedCount > 0) {
                    call.respond(mapOf("message" to "Режим суммирования установлен и обработка начата"))
                } else {
                    call.respond(HttpStatusCode.InternalServerError, "Не удалось изменить режим")
                }
            }
            "questions_original_text" -> {
                booksCollection.updateOne(
                    Filters.eq("_id", ObjectId(idBook)),
                    Updates.set("mode", mode)
                )
                call.respond(mapOf("message" to "Режим вопросов по оригинальному тексту установлен"))
            }
            "retelling" -> {
                // Извлечение пересказа книги из базы данных
                val retelling = BackgroundProcessing.getBookRetelling(idBook)
                call.respond(mapOf("retelling" to retelling))
            }
            "test" -> {
                // Генерация вопросов и ответов по всей книге
                val test = BackgroundProcessing.generateTestForBook(idBook)
                call.respond(test)
            }
            "similar_books" -> {
                // Рекомендации похожих книг
                val recommendations = BackgroundProcessing.getSimilarBooks(idBook)
                call.respond(recommendations)
            }
            else -> {
                call.respond(HttpStatusCode.BadRequest, "Неизвестный режим")
            }
        }
    }

    get("/get_book_detail") {
        val bookId = call.request.queryParameters["id"]

        if (bookId.isNullOrEmpty()) {
            call.application.environment.log.info("ID книги не предоставлен.")
            call.respond(
                HttpStatusCode.BadRequest,
                BookResponse(
                    status = "error",
                    message = "Не предоставлен ID книги"
                )
            )
            return@get
        }

        try {
            // Логируем ID книги
            call.application.environment.log.info("Получен запрос на книгу с ID: $bookId")

            // Преобразуем строковый ID в ObjectId и проверяем формат
            val objectId = try {
                ObjectId(bookId)
            } catch (e: IllegalArgumentException) {
                call.application.environment.log.info("Неверный формат ID: $bookId")
                call.respond(
                    HttpStatusCode.BadRequest,
                    BookResponse(
                        status = "error",
                        message = "Неверный формат ID книги"
                    )
                )
                return@get
            }

            // Получаем коллекции книг и текстовых блоков
            val booksCollection: MongoCollection<Document> = DatabaseFactory.getBooksCollection()
            val textBlocksCollection: MongoCollection<Document> = DatabaseFactory.getTextBlocksCollection()

            // Находим книгу по её ObjectId
            val bookDoc = booksCollection.find(Filters.eq("_id", objectId)).firstOrNull()

            if (bookDoc == null) {
                call.application.environment.log.info("Книга с ID: $bookId не найдена.")
                call.respond(
                    HttpStatusCode.NotFound,
                    BookResponse(
                        status = "error",
                        message = "Книга не найдена"
                    )
                )
                return@get
            }

            val book = bookDoc.toBook()

            // Логируем содержимое textBlockIds
            call.application.environment.log.info("textBlockIds в книге: ${book.textBlockIds}")

            // Преобразуем textBlockIds из книги в ObjectId для запроса
            val objectIdList = book.textBlockIds.map { ObjectId(it) }  // Преобразуем textBlockIds в ObjectId

            // Запрашиваем все текстовые блоки по их _id
            val textBlockDocs = textBlocksCollection.find(Filters.`in`("_id", objectIdList)).toList()

            // Логируем количество найденных текстовых блоков
            call.application.environment.log.info("Найдено текстовых блоков: ${textBlockDocs.size}")

            // Преобразуем документы текстовых блоков в объекты TextBlock
            val textBlocks = textBlockDocs.map { it.toTextBlock() }

            // Логируем пример содержимого текстовых блоков
            call.application.environment.log.info("Пример содержимого первого блока: ${textBlocks.firstOrNull()?.original ?: "Блоки не найдены"}")

            // Создаем ответ, включая аннотацию книги и содержимое текстовых блоков
            val response = BookDetailResponse(
                annotation = book.annotation ?: "",
                totalPages = textBlocks.size,
                textBlocks = textBlocks.map { it.original } // Возвращаем содержимое блоков
            )

            // Отправляем ответ
            call.respond(
                HttpStatusCode.OK,
                response
            )
        } catch (e: Exception) {
            // Логируем общую ошибку
            call.application.environment.log.error("Ошибка: ${e.message}")
            call.respond(
                HttpStatusCode.InternalServerError,
                BookResponse(
                    status = "error",
                    message = "Внутренняя ошибка сервера: ${e.message}"
                )
            )
        }
    }


    get("/get_book_page") {
        val bookId = call.request.queryParameters["id"]
        val pageNumberParam = call.request.queryParameters["page"]

        if (bookId.isNullOrEmpty() || pageNumberParam.isNullOrEmpty()) {
            call.respond(
                HttpStatusCode.BadRequest,
                mapOf("status" to "error", "message" to "Не предоставлены ID книги или номер страницы")
            )
            return@get
        }

        val pageNumber = pageNumberParam.toIntOrNull()
        if (pageNumber == null || pageNumber < 1) {
            call.respond(
                HttpStatusCode.BadRequest,
                mapOf("status" to "error", "message" to "Неверный номер страницы")
            )
            return@get
        }

        try {
            val booksCollection: MongoCollection<Document> = DatabaseFactory.getBooksCollection()
            val bookDoc = booksCollection.find(Filters.eq("_id", ObjectId(bookId))).firstOrNull()

            if (bookDoc == null) {
                call.respond(
                    HttpStatusCode.NotFound,
                    mapOf("status" to "error", "message" to "Книга не найдена")
                )
                return@get
            }

            val book = bookDoc.toBook()

            if (pageNumber > book.textBlockIds.size) {
                call.respond(
                    HttpStatusCode.NotFound,
                    mapOf("status" to "error", "message" to "Страница не найдена")
                )
                return@get
            }

            val textBlockId = book.textBlockIds[pageNumber - 1]
            val textBlocksCollection: MongoCollection<Document> = DatabaseFactory.getTextBlocksCollection()

            // Ищем по строковому значению _id
            val textBlockDoc = textBlocksCollection.find(Filters.eq("_id", ObjectId(textBlockId))).firstOrNull()

            if (textBlockDoc == null) {
                call.respond(
                    HttpStatusCode.NotFound,
                    mapOf("status" to "error", "message" to "Страница не найдена")
                )
                return@get
            }

            val textBlock = textBlockDoc.toTextBlock()

            val response = BookPageResponse(
                pageNumber = pageNumber,
                totalPages = book.textBlockIds.size,
                content = textBlock.original
            )

            call.respond(
                HttpStatusCode.OK,
                response
            )
        } catch (e: IllegalArgumentException) {
            // Неверный формат ID книги
            call.respond(
                HttpStatusCode.BadRequest,
                mapOf("status" to "error", "message" to "Неверный формат ID книги или ID блока")
            )
        } catch (e: Exception) {
            // Общая ошибка
            call.respond(
                HttpStatusCode.InternalServerError,
                mapOf("status" to "error", "message" to "Внутренняя ошибка сервера: ${e.message}")
            )
        }
    }
}

fun isSupportedMimeType(mimeType: String): Boolean {
    return mimeType == "application/pdf" ||
            mimeType == "application/fb2+xml" ||
            mimeType == "text/plain"
}

fun getSupportedFileType(part: PartData.FileItem, fileName: String): String? {
    val mimeTypes = setOf("application/pdf", "application/fb2+xml", "text/plain")
    var fileType = part.contentType?.toString()
    if (fileType == null || !mimeTypes.contains(fileType)) {
        fileType = when (fileName.substringAfterLast('.', "").lowercase()) {
            "pdf" -> "application/pdf"
            "fb2" -> "application/fb2+xml"
            "txt" -> "text/plain"
            else -> null
        }
    }
    return if (isSupportedMimeType(fileType ?: "")) fileType else null
}

suspend fun saveFile(part: PartData.FileItem, uploadDir: File, fileName: String): File? {
    val filePath = File(uploadDir, fileName)
    return try {
        val byteReadChannel = part.provider()
        withContext(Dispatchers.IO) {
            filePath.outputStream().use { outputStream ->
                byteReadChannel.copyTo(outputStream)
            }
        }
        filePath
    } catch (e: Exception) {
        null
    }
}