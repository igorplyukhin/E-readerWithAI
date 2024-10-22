package com.example.libapp.models

data class Book(
    val idBook: String,
    val title: String,
    val author: String,
    val description: String,
    val annotation: String?,
    val nameFile: String,
    val filePath: String,
)
