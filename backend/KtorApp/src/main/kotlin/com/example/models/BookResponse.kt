package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class BookResponse(
    val status: String,
    val message: String,
    val book: Book? = null // Добавлено поле book
)