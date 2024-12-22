package com.example.libapp.viewmodels

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.example.libapp.models.Book
import com.example.libapp.repositories.BookRepository

class BookViewModel : ViewModel() {

    private val bookRepository = BookRepository()

    private val _books = MutableLiveData<List<Book>>()
    val books: LiveData<List<Book>> get() = _books

    fun loadAllBooks() {
        bookRepository.getAllBooks { books ->
            Log.d("BookViewModel", "Загружено всех книг: ${books.size}")
            _books.postValue(books)
        }
    }

    fun loadFavoriteBooks() {
        bookRepository.getFavoriteBooks { books ->
            Log.d("BookViewModel", "Загружено избранных книг: ${books.size}")
            _books.postValue(books)
        }
    }
}
