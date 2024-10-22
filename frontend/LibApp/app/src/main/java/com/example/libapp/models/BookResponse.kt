package com.example.libapp.models

data class BookResponse(
    val status: String,
    val message: String,
    val book: Book? = null // Добавлено поле book
)
