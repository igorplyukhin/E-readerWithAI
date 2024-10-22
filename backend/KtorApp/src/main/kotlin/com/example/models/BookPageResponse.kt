package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class BookPageResponse(
    val pageNumber: Int,
    val totalPages: Int,
    val content: String
)