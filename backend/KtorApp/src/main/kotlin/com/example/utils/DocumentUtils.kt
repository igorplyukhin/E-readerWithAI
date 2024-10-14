package com.example.utils

import org.bson.Document
import com.example.models.User
import com.example.models.Book
import com.example.models.TextBlock
import org.bson.types.ObjectId

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
    return Book(
        idBook = getObjectId("_id").toString(),
        title = getString("title") ?: "",
        author = getString("author") ?: "",
        description = getString("description") ?: "",
        status = getString("status") ?: "reading",
        mode = getString("mode") ?: "default",
        nameFile = getString("nameFile") ?: "",
        filePath = getString("filePath") ?: "",
        blockStopBook = getInteger("blockStopBook", 0),
        chapterStopBook = getInteger("chapterStopBook", 0),
        textBlockIds = getList("textBlockIds", String::class.java) ?: emptyList()
    )
}

// Преобразование Book в Document (без userId)
fun Book.toDocument(): Document {
    return Document("_id", ObjectId(idBook))
        .append("title", title)
        .append("author", author)
        .append("description", description)
        .append("status", status)
        .append("mode", mode)
        .append("nameFile", nameFile)
        .append("filePath", filePath)
        .append("blockStopBook", blockStopBook)
        .append("chapterStopBook", chapterStopBook)
        .append("textBlockIds", textBlockIds)
}


// Преобразование Document в TextBlock
fun Document.toTextBlock(): TextBlock {
    return TextBlock(
        idBlock = getString("_id") ?: throw IllegalArgumentException("TextBlock _id is missing"),
        original = getString("original") ?: "",
        numberChapter = getInteger("numberChapter", 0),
        summary = getString("summary"),
        summaryTime = getString("summaryTime"),
        questions = getList("questions", String::class.java) ?: emptyList(),
        rightAnswers = getList("rightAnswers", String::class.java) ?: emptyList()
    )
}

// Преобразование TextBlock в Document
fun TextBlock.toDocument(): Document {
    return Document("_id", idBlock)
        .append("original", original)
        .append("numberChapter", numberChapter)
        .append("summary", summary)
        .append("summaryTime", summaryTime)
        .append("questions", questions)
        .append("rightAnswers", rightAnswers)
}
