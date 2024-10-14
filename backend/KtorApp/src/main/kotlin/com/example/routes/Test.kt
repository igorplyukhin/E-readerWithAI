package com.example.routes

import io.ktor.server.routing.*
import io.ktor.server.response.*
import io.ktor.http.*
import com.example.utils.DatabaseFactory

fun Route.healthRoutes() {
    post("/health") {
        try {
            val usersCollection = DatabaseFactory.getUsersCollection()
            val count = usersCollection.countDocuments()
            call.respond(HttpStatusCode.OK, mapOf("message" to "Connected to MongoDB. Users count: $count"))
        } catch (e: Exception) {
            call.respond(HttpStatusCode.InternalServerError, mapOf("error" to "Failed to connect to MongoDB"))
        }
    }
}
