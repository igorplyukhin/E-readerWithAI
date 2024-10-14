package com.example.routes

import io.ktor.server.routing.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.http.*
import com.example.utils.DatabaseFactory
import com.example.utils.BackgroundProcessing
import com.example.utils.toBook
import com.example.utils.toTextBlock
import com.mongodb.client.model.Updates
import org.bson.Document

fun Route.textRoutes() {

    // Маршрут для получения текста в зависимости от текущего режима
    post("/get_text") {
        val parameters = call.receiveParameters()
        val idUser = parameters["id_user"]
        val idBook = parameters["id_book"]

        if (idUser == null || idBook == null) {
            call.respond(HttpStatusCode.BadRequest, "ID пользователя или книги не предоставлен")
            return@post
        }

        val booksCollection = DatabaseFactory.getBooksCollection()
        val bookDoc = booksCollection.find(
            Document("_id", idBook).append("userId", idUser)
        ).firstOrNull()

        if (bookDoc == null) {
            call.respond(HttpStatusCode.NotFound, "Книга не найдена или не принадлежит пользователю")
            return@post
        }

        val book = bookDoc.toBook()
        val currentBlockIndex = book.blockStopBook
        val idBlock = book.textBlockIds.getOrNull(currentBlockIndex)

        if (idBlock == null) {
            call.respond(HttpStatusCode.NotFound, "Текстовый блок не найден")
            return@post
        }

        val textBlocksCollection = DatabaseFactory.getTextBlocksCollection()
        val textBlockDoc = textBlocksCollection.find(Document("_id", idBlock)).firstOrNull()

        if (textBlockDoc == null) {
            call.respond(HttpStatusCode.NotFound, "Текстовый блок не найден")
            return@post
        }

        val textBlock = textBlockDoc.toTextBlock()

        when (book.mode) {
            "summarization_time" -> {
                // Если суммированный текст с учетом времени не готов, запускаем фоновую обработку
                if (textBlock.summaryTime == null) {
                    // Запускаем фоновую обработку
                    BackgroundProcessing.processSummarizationForBlock(textBlock, mode = "summarization_time")
                    call.respond(HttpStatusCode.Accepted, "Суммирование с учетом времени чтения запущено. Попробуйте позже.")
                } else {
                    call.respond(mapOf("text" to textBlock.summaryTime, "id_block" to idBlock))
                }
            }
            "summarization" -> {
                // Если суммированный текст не готов, запускаем фоновую обработку
                if (textBlock.summary == null) {
                    // Запускаем фоновую обработку
                    BackgroundProcessing.processSummarizationForBlock(textBlock, mode = "summarization")
                    call.respond(HttpStatusCode.Accepted, "Суммирование запущено. Попробуйте позже.")
                } else {
                    call.respond(mapOf("text" to textBlock.summary, "id_block" to idBlock))
                }
            }
            "questions_original_text" -> {
                call.respond(mapOf("text" to textBlock.original, "id_block" to idBlock))
            }
            else -> {
                call.respond(HttpStatusCode.BadRequest, "Неверный режим книги")
            }
        }
    }

    // Маршрут для получения вопросов по текстовому блоку
    post("/get_questions") {
        val parameters = call.receiveParameters()
        val idUser = parameters["id_user"]
        val idBook = parameters["id_book"]
        val idBlock = parameters["id_block"]

        if (idUser == null || idBook == null || idBlock == null) {
            call.respond(HttpStatusCode.BadRequest, "Не предоставлены необходимые параметры")
            return@post
        }

        val booksCollection = DatabaseFactory.getBooksCollection()
        val bookDoc = booksCollection.find(
            Document("_id", idBook).append("userId", idUser)
        ).firstOrNull()

        if (bookDoc == null) {
            call.respond(HttpStatusCode.NotFound, "Книга не найдена или не принадлежит пользователю")
            return@post
        }

        val textBlocksCollection = DatabaseFactory.getTextBlocksCollection()
        val textBlockDoc = textBlocksCollection.find(Document("_id", idBlock)).firstOrNull()

        if (textBlockDoc == null) {
            call.respond(HttpStatusCode.NotFound, "Текстовый блок не найден")
            return@post
        }

        val textBlock = textBlockDoc.toTextBlock()

        if (textBlock.questions.isEmpty()) {
            // Генерируем вопросы и ответы
            val (questions, answers) = BackgroundProcessing.generateQuestionsForBlock(textBlock.original)
            // Обновляем текстовый блок в базе данных
            textBlocksCollection.updateOne(
                Document("_id", idBlock),
                Updates.combine(
                    Updates.set("questions", questions),
                    Updates.set("rightAnswers", answers)
                )
            )
            call.respond(mapOf("questions" to questions, "answers" to answers))
        } else {
            call.respond(mapOf("questions" to textBlock.questions, "answers" to textBlock.rightAnswers))
        }
    }

    // Маршрут для перехода к следующему блоку текста
    post("/next_block_text") {
        val parameters = call.receiveParameters()
        val idUser = parameters["id_user"]
        val idBook = parameters["id_book"]

        if (idUser == null || idBook == null) {
            call.respond(HttpStatusCode.BadRequest, "ID пользователя или книги не предоставлен")
            return@post
        }

        val booksCollection = DatabaseFactory.getBooksCollection()
        val bookDoc = booksCollection.find(
            Document("_id", idBook).append("userId", idUser)
        ).firstOrNull()

        if (bookDoc == null) {
            call.respond(HttpStatusCode.NotFound, "Книга не найдена или не принадлежит пользователю")
            return@post
        }

        val book = bookDoc.toBook()
        val nextBlockIndex = book.blockStopBook + 1
        if (nextBlockIndex >= book.textBlockIds.size) {
            call.respond(HttpStatusCode.BadRequest, "Это последний блок текста")
            return@post
        }

        booksCollection.updateOne(
            Document("_id", idBook),
            Updates.set("blockStopBook", nextBlockIndex)
        )
        call.respond(mapOf("message" to "Переход к следующему блоку выполнен"))
    }

    // Маршрут для перехода к предыдущему блоку текста
    post("/back_block_text") {
        val parameters = call.receiveParameters()
        val idUser = parameters["id_user"]
        val idBook = parameters["id_book"]

        if (idUser == null || idBook == null) {
            call.respond(HttpStatusCode.BadRequest, "ID пользователя или книги не предоставлен")
            return@post
        }

        val booksCollection = DatabaseFactory.getBooksCollection()
        val bookDoc = booksCollection.find(
            Document("_id", idBook).append("userId", idUser)
        ).firstOrNull()

        if (bookDoc == null) {
            call.respond(HttpStatusCode.NotFound, "Книга не найдена или не принадлежит пользователю")
            return@post
        }

        val book = bookDoc.toBook()
        val previousBlockIndex = book.blockStopBook - 1
        if (previousBlockIndex < 0) {
            call.respond(HttpStatusCode.BadRequest, "Это первый блок текста")
            return@post
        }

        booksCollection.updateOne(
            Document("_id", idBook),
            Updates.set("blockStopBook", previousBlockIndex)
        )
        call.respond(mapOf("message" to "Переход к предыдущему блоку выполнен"))
    }
}
