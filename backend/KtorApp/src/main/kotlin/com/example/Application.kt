package com.example

import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import com.example.utils.DatabaseFactory
import io.ktor.server.routing.*
import com.example.routes.*
import io.ktor.http.ContentType
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.response.respondText

fun main() {
    // Инициализация сервера Ktor
    embeddedServer(Netty, port = 8080, host = "0.0.0.0") {
        // Инициализация приложения
        configureSerialization()
        configureRouting()
        configureDatabase()
    }.start(wait = true)
}

// Функция для настройки сериализации JSON
fun Application.configureSerialization() {
    install(ContentNegotiation) {
        json()
    }
}

fun Application.configureRouting() {
    routing {
        // Добавляем маршрут для корневого пути "/"
        get("/") {
            call.respondText("Hello World!", ContentType.Text.Plain)
        }

        healthRoutes()

        // Существующие маршруты
        userRoutes()
        bookRoutes()
        textRoutes()
        // Вы можете добавить дополнительные маршруты здесь
    }
}

// Функция для инициализации базы данных
fun Application.configureDatabase() {
    DatabaseFactory.init()
}
