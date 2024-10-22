package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class UserBooksResponse(
    val count_book: Int,
    val books: List<Book>
)
