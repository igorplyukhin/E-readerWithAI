package com.example.routes

import io.ktor.server.routing.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.http.*
import com.example.utils.*
import com.example.utils.toBook
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

        multipart.forEachPart { part ->
            when (part) {
                is PartData.FormItem -> {
                    if (part.name == "id") {
                        userId = part.value
                    }
                }
                is PartData.FileItem -> {
                    if (part.name == "file") {
                        fileName = part.originalFileName ?: "default.txt"
                        val uploadDir = File("uploads")
                        if (!uploadDir.exists()) {
                            uploadDir.mkdirs()
                        }
                        val filePath = File(uploadDir, fileName)

                        // Асинхронное копирование данных из ByteReadChannel в файл
                        val byteReadChannel = part.provider()
                        withContext(Dispatchers.IO) {
                            filePath.outputStream().use { outputStream ->
                                byteReadChannel.copyTo(outputStream)
                            }
                        }
                    }
                }
                else -> {}
            }
            part.dispose()
        }

        if (userId == null || fileName == null) {
            call.respond(HttpStatusCode.BadRequest, "Не предоставлен файл или ID пользователя")
            return@post
        }

        val filePath = "uploads/$fileName"
        val convertedFilePath = try {
            FileUtils.checkAndConvertFile(filePath)
        } catch (e: Exception) {
            call.respond(HttpStatusCode.BadRequest, "Ошибка при обработке файла: ${e.message}")
            return@post
        }

        // Сохранение метаданных книги в MongoDB
        val booksCollection = DatabaseFactory.getBooksCollection()
        val book = Document()
            .append("fileName", fileName)
            .append("filePath", convertedFilePath)
        booksCollection.insertOne(book)

        val fileId = book["_id"].toString()

        // Обновление массива bookIds у пользователя
        val usersCollection = DatabaseFactory.getUsersCollection()
        usersCollection.updateOne(
            Filters.eq("_id", userId),
            Updates.addToSet("bookIds", fileId)
        )

        call.respond(
            HttpStatusCode.OK,
            mapOf(
                "status" to "success",
                "message" to "Книга успешно загружена и обработка начата",
                "fileId" to fileId
            )
        )
    }

    // Маршрут для получения информации о книге
    post("/get_book") {
        val parameters = call.receiveParameters()
        val idBook = parameters["id_book"]

        if (idBook == null) {
            call.respond(HttpStatusCode.BadRequest, "ID книги не предоставлен")
            return@post
        }

        val booksCollection = DatabaseFactory.getBooksCollection()
        val bookDoc = booksCollection.find(Filters.eq("_id", ObjectId(idBook))).firstOrNull()

        if (bookDoc != null) {
            val book = bookDoc.toBook()
            call.respond(book)
        } else {
            call.respond(HttpStatusCode.NotFound, "Книга не найдена")
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
                booksCollection.updateOne(
                    Filters.eq("_id", ObjectId(idBook)),
                    Updates.set("mode", mode)
                )
                call.respond(mapOf("message" to "Режим суммирования установлен и обработка начата"))
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

    // Дополнительные маршруты можно добавить здесь
}
