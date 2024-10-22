package com.example.models

import kotlinx.serialization.Contextual
import kotlinx.serialization.Serializable
import org.bson.Document
import org.bson.types.ObjectId

@Serializable
data class Book(
    val idBook: String = ObjectId().toHexString(), // Используем toHexString()
    val title: String,
    val author: String,
    val description: String,
    val annotation: String? = null,
    val status: String = "reading",
    val mode: String = "default",
    val nameFile: String,
    val filePath: String,
    val blockStopBook: Int = 0,
    val chapterStopBook: Int = 0,
    val textBlockIds: List<String> = emptyList() // Изменено на List<String>
) {
    fun toDocument(): Document {
        return Document("_id", ObjectId(idBook))
            .append("title", title)
            .append("author", author)
            .append("description", description)
            .append("annotation", annotation)
            .append("status", status)
            .append("mode", mode)
            .append("nameFile", nameFile)
            .append("filePath", filePath)
            .append("blockStopBook", blockStopBook)
            .append("chapterStopBook", chapterStopBook)
            .append("textBlockIds", textBlockIds.map { ObjectId(it) }) // Преобразуем строки обратно в ObjectId при сохранении
    }
}
