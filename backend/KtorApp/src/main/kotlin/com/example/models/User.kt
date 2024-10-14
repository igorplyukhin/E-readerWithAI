package com.example.models

data class User(
    val idUser: String,
    val password: String = "",
    val bookIds: List<String> = emptyList(),
    val countBook: Int = 0
)
