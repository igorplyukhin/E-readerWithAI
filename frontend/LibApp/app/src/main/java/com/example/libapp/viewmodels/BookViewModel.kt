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

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> get() = _error

    fun loadUserBooks(userId: String) {
        bookRepository.getUserBooks(userId, { books ->
            Log.d("BookViewModel", "Загружено книг пользователя: ${books.size}")
            _books.postValue(books)
        }, { errorMessage ->
            Log.e("BookViewModel", "Ошибка загрузки книг: $errorMessage")
            _error.postValue(errorMessage)
        })
    }
}
