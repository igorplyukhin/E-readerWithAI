package com.example.models

data class TextBlock(
    val idBlock: String,
    val original: String,
    val numberChapter: Int,
    val summary: String? = null,
    val summaryTime: String? = null,
    val questions: List<String> = emptyList(),
    val rightAnswers: List<String> = emptyList()
)
