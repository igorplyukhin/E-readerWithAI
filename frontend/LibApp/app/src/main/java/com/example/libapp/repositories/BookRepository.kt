package com.example.libapp.repositories

import android.util.Log
import com.example.libapp.models.Book

class BookRepository {

    private val allBooks = listOf(
        Book(
            idBook = "1", // Уникальный идентификатор книги
            title = "Книга 1",
            author = "Автор 1",
            description = "Описание книги 1",
            annotation = "Аннотация книги 1",
            nameFile = "book1.pdf",
            filePath = "/path/to/book1.pdf",
            progress = 30,
            status = "4 час 37 мин"
        ),
        Book(
            idBook = "2", // Уникальный идентификатор книги
            title = "Книга 2",
            author = "Автор 2",
            description = "Описание книги 2",
            annotation = "Аннотация книги 2",
            nameFile = "book2.pdf",
            filePath = "/path/to/book2.pdf",
            progress = 50,
            status = "2 час 37 мин"
        ),
        Book(
            idBook = "3", // Уникальный идентификатор книги
            title = "Книга 3",
            author = "Автор 3",
            description = "Описание книги 3",
            annotation = "Аннотация книги 3",
            nameFile = "book3.pdf",
            filePath = "/path/to/book3.pdf",
            progress = 56,
            status = "2 час 40 мин"
        ),
        Book(
            idBook = "4", // Уникальный идентификатор книги
            title = "Книга 4",
            author = "Автор 4",
            description = "Описание книги 4",
            annotation = "Аннотация книги 4",
            nameFile = "book4.pdf",
            filePath = "/path/to/book4.pdf",
            progress = 67,
            status = "2 часа"
        ),
        Book(
            idBook = "5", // Уникальный идентификатор книги
            title = "Книга 5",
            author = "Автор 5",
            description = "Описание книги 5",
            annotation = "Аннотация книги 5",
            nameFile = "book5.pdf",
            filePath = "/path/to/book5.pdf",
            progress = 37,
            status = "3 час 23 мин"
        ),
        Book(
            idBook = "6", // Уникальный идентификатор книги
            title = "Книга 6",
            author = "Автор 6",
            description = "Описание книги 6",
            annotation = "Аннотация книги 6",
            nameFile = "book6.pdf",
            filePath = "/path/to/book6.pdf",
            progress = 75,
            status = "1 час 19 мин"
        )

    )

    private val favoriteBooks = listOf(
        Book(
            idBook = "2", // Идентификатор той же книги, что и в allBooks
            title = "Книга 2",
            author = "Автор 2",
            description = "Описание книги 2",
            annotation = "Аннотация книги 2",
            nameFile = "book2.pdf",
            filePath = "/path/to/book2.pdf",
            progress = 50,
            status = "2 час 37 мин"
        ),
        Book(
            idBook = "4", // Уникальный идентификатор книги
            title = "Книга 4",
            author = "Автор 4",
            description = "Описание книги 4",
            annotation = "Аннотация книги 4",
            nameFile = "book4.pdf",
            filePath = "/path/to/book4.pdf",
            progress = 67,
            status = "2 часа"
        ),
        Book(
            idBook = "5", // Уникальный идентификатор книги
            title = "Книга 5",
            author = "Автор 5",
            description = "Описание книги 5",
            annotation = "Аннотация книги 5",
            nameFile = "book5.pdf",
            filePath = "/path/to/book5.pdf",
            progress = 37,
            status = "3 час 23 мин"
        ),
        Book(
            idBook = "6", // Уникальный идентификатор книги
            title = "Книга 6",
            author = "Автор 6",
            description = "Описание книги 6",
            annotation = "Аннотация книги 6",
            nameFile = "book6.pdf",
            filePath = "/path/to/book6.pdf",
            progress = 75,
            status = "1 час 19 мин"
        )
    )

    fun getAllBooks(callback: (List<Book>) -> Unit) {
        Log.d("BookRepository", "Возвращаем список всех книг: ${allBooks.size} книг")
        callback(allBooks)
    }

    fun getFavoriteBooks(callback: (List<Book>) -> Unit) {
        Log.d("BookRepository", "Возвращаем список избранных книг: ${favoriteBooks.size} книг")
        callback(favoriteBooks)
    }
}


