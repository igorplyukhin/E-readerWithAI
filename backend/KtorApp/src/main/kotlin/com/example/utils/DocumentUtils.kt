package com.example.utils

import org.bson.Document
import com.example.models.User
import com.example.models.Book
import com.example.models.TextBlock
import org.slf4j.LoggerFactory

// Преобразование Document в User
fun Document.toUser(): User {
    val idUser = getString("_id") ?: throw IllegalArgumentException("User _id is missing")
    val password = getString("password") ?: ""
    val bookIds = getList("bookIds", String::class.java) ?: emptyList()
    val countBook = getInteger("countBook", 0)
    return User(idUser, password, bookIds, countBook)
}

// Преобразование User в Document
fun User.toDocument(): Document {
    return Document("_id", idUser)
        .append("password", password)
        .append("bookIds", bookIds)
        .append("countBook", countBook)
}

// Преобразование Document в Book (без userId)
fun Document.toBook(): Book {
    val logger = LoggerFactory.getLogger("toBook")

    val annotation = getString("annotation")
    val textBlockIds = getList("textBlockIds", String::class.java) ?: emptyList()

    logger.info("Mapping Document to Book: annotation=$annotation, textBlockIds.size=${textBlockIds.size}")
    logger.info("First 5 textBlockIds: ${textBlockIds.take(5)}")

    return Book(
        idBook = getObjectId("_id").toHexString(), // Используем _id как идентификатор
        title = getString("title") ?: throw IllegalArgumentException("title missing"),
        author = getString("author") ?: throw IllegalArgumentException("author missing"),
        description = getString("description") ?: throw IllegalArgumentException("description missing"),
        annotation = annotation,
        status = getString("status") ?: "reading",
        mode = getString("mode") ?: "default",
        nameFile = getString("nameFile") ?: throw IllegalArgumentException("nameFile missing"),
        filePath = getString("filePath") ?: throw IllegalArgumentException("filePath missing"),
        blockStopBook = getInteger("blockStopBook") ?: 0,
        chapterStopBook = getInteger("chapterStopBook") ?: 0,
        textBlockIds = textBlockIds
    )
}

// Преобразование Document в TextBlock
fun Document.toTextBlock(): TextBlock {
    return TextBlock(
        _id = getObjectId("_id").toHexString() ?: throw IllegalArgumentException("TextBlock _id is missing"),
        original = getString("original") ?: "",
        numberChapter = getInteger("numberChapter", 0),
        summary = getString("summary"),
        summaryTime = getString("summaryTime"),
        questions = getList("questions", String::class.java) ?: emptyList(),
        rightAnswers = getList("rightAnswers", String::class.java) ?: emptyList()
    )
}


