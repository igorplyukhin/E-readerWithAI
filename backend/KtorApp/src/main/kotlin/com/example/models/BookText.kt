package com.example.models

data class BookText(
    val title: String,
    val authors: String,
    val content: String,
    val annotation: String? = null // Добавлено поле annotation
)