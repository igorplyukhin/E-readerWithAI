package com.example.libapp.repositories

import android.util.Log
import com.example.libapp.api.ApiClient
import com.example.libapp.models.Book
import com.example.libapp.models.UserBooksResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class BookRepository {

    fun getUserBooks(userId: String, callback: (List<Book>) -> Unit, onError: (String) -> Unit) {
        ApiClient.instance.getUser(userId).enqueue(object : Callback<UserBooksResponse> {
            override fun onResponse(call: Call<UserBooksResponse>, response: Response<UserBooksResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val books = response.body()?.books ?: emptyList()
                    Log.d("BookRepository", "Получено книг: ${books.size}")
                    callback(books)
                } else {
                    val errorMessage = response.errorBody()?.string() ?: response.message()
                    Log.e("BookRepository", "Ошибка загрузки книг: $errorMessage")
                    onError(errorMessage)
                }
            }

            override fun onFailure(call: Call<UserBooksResponse>, t: Throwable) {
                Log.e("BookRepository", "Ошибка сети: ${t.message}", t)
                onError("Ошибка сети: ${t.message}")
            }
        })
    }
}
