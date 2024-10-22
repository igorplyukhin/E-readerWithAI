package com.example.libapp.models

data class BookDetailResponse(
    val annotation: String?,
    val totalPages: Int,
    val textBlocks: List<String> // Должна быть идентична
)