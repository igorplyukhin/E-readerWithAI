package com.example.models

import kotlinx.serialization.Serializable
import org.bson.Document
import org.bson.types.ObjectId

@Serializable
data class TextBlock(
    val _id: String, // Используем _id вместо idBlock
    val original: String,
    val numberChapter: Int = 0,
    val summary: String? = null,
    val summaryTime: String? = null,
    val questions: List<String> = emptyList(),
    val rightAnswers: List<String> = emptyList()
) {
    fun toDocument(): Document {
        return Document("_id", ObjectId(_id)) // Используем _id вместо idBlock
            .append("original", original)
            .append("numberChapter", numberChapter)
            .append("summary", summary)
            .append("summaryTime", summaryTime)
            .append("questions", questions)
            .append("rightAnswers", rightAnswers)
    }
}

