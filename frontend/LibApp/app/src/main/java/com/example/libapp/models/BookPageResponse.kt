package com.example.libapp.models

data class BookPageResponse(
    val pageNumber: Int,
    val totalPages: Int,
    val content: String
)