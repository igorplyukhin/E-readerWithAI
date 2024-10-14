package com.example.routes

import io.ktor.server.routing.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.http.*
import com.example.utils.DatabaseFactory
import com.example.models.*
import com.example.utils.toBook
import com.example.utils.toUser
import com.example.utils.toDocument
import com.mongodb.client.model.Filters
import org.bson.Document
import org.bson.types.ObjectId

fun Route.userRoutes() {

    // Маршрут для получения информации о пользователе и его книгах
    post("/get_user") {
        val parameters = call.receiveParameters()
        val login = parameters["login"]

        if (login == null) {
            call.respond(HttpStatusCode.BadRequest, "Логин не предоставлен")
            return@post
        }

        val usersCollection = DatabaseFactory.getUsersCollection()
        val userDoc = usersCollection.find(Filters.eq("_id", login)).firstOrNull()

        if (userDoc != null) {
            val user = userDoc.toUser()
            val booksCollection = DatabaseFactory.getBooksCollection()
            val books = booksCollection.find(Filters.`in`("_id", user.bookIds.map { ObjectId(it) }))
                .map { it.toBook() }
                .toList()

            val response = UserBooksResponse(
                count_book = books.size,
                books = books
            )
            call.respond(response)
        } else {
            // Создаем нового пользователя
            val newUser = User(idUser = login)
            usersCollection.insertOne(newUser.toDocument())

            val response = UserBooksResponse(
                count_book = 0,
                books = emptyList()
            )
            call.respond(response)
        }
    }


    // Маршрут для получения списка книг пользователя
    post("/get_user_books") {
        val parameters = call.receiveParameters()
        val userId = parameters["id"]

        if (userId == null) {
            call.respond(HttpStatusCode.BadRequest, "User ID not provided")
            return@post
        }

        val usersCollection = DatabaseFactory.getUsersCollection()
        val userDoc = usersCollection.find(Filters.eq("_id", userId)).firstOrNull()

        if (userDoc != null) {
            val user = userDoc.toUser()
            val booksCollection = DatabaseFactory.getBooksCollection()
            val books = booksCollection.find(Filters.`in`("_id", user.bookIds.map { ObjectId(it) }))
                .map { it.toBook() }
                .toList()

            if (books.isNotEmpty()) {
                call.respond(HttpStatusCode.OK, books)
            } else {
                call.respond(HttpStatusCode.NotFound, mapOf("status" to "error", "message" to "No books found for this user"))
            }
        } else {
            call.respond(HttpStatusCode.NotFound, "User not found")
        }
    }

    // Маршрут для регистрации нового пользователя
    post("/register") {
        val parameters = call.receiveParameters()
        val login = parameters["login"]
        val password = parameters["password"]

        if (login == null || password == null) {
            call.respond(HttpStatusCode.BadRequest, mapOf("status" to "error", "message" to "Логин или пароль не предоставлены"))
            return@post
        }

        val usersCollection = DatabaseFactory.getUsersCollection()
        val existingUser = usersCollection.find(Filters.eq("_id", login)).firstOrNull()

        if (existingUser != null) {
            call.respond(HttpStatusCode.Conflict, mapOf("status" to "error", "message" to "Пользователь с таким логином уже существует"))
            return@post
        }

        val newUser = User(idUser = login, password = password)
        usersCollection.insertOne(newUser.toDocument())

        call.respond(HttpStatusCode.Created, mapOf("status" to "success", "message" to "Пользователь успешно зарегистрирован", "userId" to newUser.idUser))
    }

    // Маршрут для аутентификации пользователя
    post("/login") {
        val parameters = call.receiveParameters()
        val login = parameters["login"]
        val password = parameters["password"]

        if (login == null || password == null) {
            call.respond(
                HttpStatusCode.BadRequest,
                mapOf("status" to "error", "message" to "Логин или пароль не предоставлены")
            )
            return@post
        }

        val usersCollection = DatabaseFactory.getUsersCollection()
        val userDoc = usersCollection.find(Filters.eq("_id", login)).firstOrNull()

        if (userDoc != null) {
            val user = userDoc.toUser()
            if (user.password == password) {
                // Возвращаем JSON с сообщением об успешной аутентификации и идентификатором пользователя
                call.respond(
                    HttpStatusCode.OK,
                    mapOf("status" to "success", "message" to "Аутентификация успешна", "userId" to user.idUser)
                )
            } else {
                call.respond(
                    HttpStatusCode.Unauthorized,
                    mapOf("status" to "error", "message" to "Неверный пароль")
                )
            }
        } else {
            call.respond(
                HttpStatusCode.NotFound,
                mapOf("status" to "error", "message" to "Пользователь не найден")
            )
        }
    }

    // Маршрут для обновления информации о пользователе
    post("/update_user") {
        val parameters = call.receiveParameters()
        val login = parameters["login"]
        val newPassword = parameters["new_password"]

        if (login == null || newPassword == null) {
            call.respond(HttpStatusCode.BadRequest, "Не предоставлены необходимые параметры")
            return@post
        }

        val usersCollection = DatabaseFactory.getUsersCollection()
        val result = usersCollection.updateOne(
            Filters.eq("_id", login),
            Document("\$set", Document("password", newPassword))
        )

        if (result.modifiedCount > 0) {
            call.respond(HttpStatusCode.OK, "Пароль успешно обновлен")
        } else {
            call.respond(HttpStatusCode.NotFound, "Пользователь не найден")
        }
    }

    // Маршрут для удаления пользователя
    post("/delete_user") {
        val parameters = call.receiveParameters()
        val login = parameters["login"]

        if (login == null) {
            call.respond(HttpStatusCode.BadRequest, "Логин не предоставлен")
            return@post
        }

        val usersCollection = DatabaseFactory.getUsersCollection()
        val result = usersCollection.deleteOne(Filters.eq("_id", login))

        if (result.deletedCount > 0) {
            call.respond(HttpStatusCode.OK, "Пользователь успешно удален")
        } else {
            call.respond(HttpStatusCode.NotFound, "Пользователь не найден")
        }
    }
}
