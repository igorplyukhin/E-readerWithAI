package com.example.models

import kotlinx.serialization.Serializable


@Serializable
data class Book(
    val idBook: String,
    val title: String,
    val author: String,
    val description: String,
    val status: String = "reading",
    val mode: String = "default",
    val nameFile: String,
    val filePath: String,
    val blockStopBook: Int = 0,
    val chapterStopBook: Int = 0,
    val textBlockIds: List<String> = emptyList()
)
