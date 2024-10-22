package com.example.libapp

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import com.example.libapp.models.BookDetailResponse
import com.example.libapp.api.ApiClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class BookAnnotationActivity : AppCompatActivity() {

    private lateinit var tvAnnotation: TextView
    private lateinit var btnRead: Button
    private lateinit var progressBar: ProgressBar

    private var bookId: String? = null
    private var totalPages: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_book_annotation)

        tvAnnotation = findViewById(R.id.tvAnnotation)
        btnRead = findViewById(R.id.btnRead)
        progressBar = findViewById(R.id.progressBar)

        bookId = intent.getStringExtra("BOOK_ID")

        if (bookId != null) {
            fetchBookDetail(bookId!!)
        } else {
            tvAnnotation.text = "Ошибка: ID книги не предоставлен."
            btnRead.isEnabled = false
        }

        btnRead.setOnClickListener {
            val intent = Intent(this, BookReadingActivity::class.java)
            intent.putExtra("BOOK_ID", bookId)
            startActivity(intent)
        }
    }

    private fun fetchBookDetail(bookId: String) {
        showLoading()

        ApiClient.instance.getBookDetail(bookId).enqueue(object : Callback<BookDetailResponse> {
            override fun onResponse(call: Call<BookDetailResponse>, response: Response<BookDetailResponse>) {
                hideLoading()
                if (response.isSuccessful) {
                    response.body()?.let { bookDetail ->
                        tvAnnotation.text = bookDetail.annotation ?: "Аннотация отсутствует."
                        totalPages = bookDetail.totalPages
                        btnRead.isEnabled = totalPages > 0
                    } ?: run {
                        tvAnnotation.text = "Не удалось получить данные о книге."
                        btnRead.isEnabled = false
                    }
                } else {
                    tvAnnotation.text = "Ошибка: ${response.message()}"
                    btnRead.isEnabled = false
                }
            }

            override fun onFailure(call: Call<BookDetailResponse>, t: Throwable) {
                hideLoading()
                tvAnnotation.text = "Ошибка сети: ${t.message}"
                btnRead.isEnabled = false
            }
        })
    }

    private fun showLoading() {
        progressBar.visibility = View.VISIBLE
        tvAnnotation.visibility = View.GONE
        btnRead.visibility = View.GONE
    }

    private fun hideLoading() {
        progressBar.visibility = View.GONE
        tvAnnotation.visibility = View.VISIBLE
        btnRead.visibility = View.VISIBLE
    }
}