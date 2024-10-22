package com.example.libapp.models

data class UserBooksResponse(
    val count_book: Int,
    val books: List<Book>
)