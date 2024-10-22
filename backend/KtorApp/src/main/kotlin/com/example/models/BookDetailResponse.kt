package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class BookDetailResponse(
    val annotation: String,
    val totalPages: Int,
    val textBlocks: List<String> // Добавляем список текстовых блоков
)