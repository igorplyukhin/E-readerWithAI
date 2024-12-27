package com.example.libapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.ImageButton
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.libapp.api.ApiClient
import com.example.libapp.models.BookDetailResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class BookDetailActivity : AppCompatActivity() {

    private lateinit var progressBar: ProgressBar
    private lateinit var tvProgress: TextView
    private var bookId: String? = null // Хранение bookId

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_book_detail)

        // Инициализация прогресс-бара и текстового поля прогресса
        progressBar = findViewById(R.id.progressBar)
        tvProgress = findViewById(R.id.tvProgress)

        // Обработка нажатия на кнопку "Назад"
        findViewById<ImageButton>(R.id.btnBack)?.setOnClickListener {
            finish() // Закрывает текущую Activity и возвращается к предыдущей
        }

        // Получение bookId из Intent
        bookId = intent.getStringExtra("BOOK_ID")
        if (bookId != null) {
            loadBookDetails(bookId!!)
        } else {
            Toast.makeText(this, "Ошибка: книга не найдена", Toast.LENGTH_SHORT).show()
            finish()
        }

        // Обработка нажатия на кнопку "Читать книгу"
        findViewById<Button>(R.id.btnReadBook)?.setOnClickListener {
            if (bookId != null) {
                // Переход к BookReadingActivity с передачей bookId
                val intent = Intent(this, BookReadingActivity::class.java)
                intent.putExtra("BOOK_ID", bookId)
                startActivity(intent)
            } else {
                Toast.makeText(this, "Ошибка: ID книги отсутствует", Toast.LENGTH_SHORT).show()
            }
        }
    }

    /**
     * Загружает информацию о книге с указанным ID с сервера.
     */
    private fun loadBookDetails(bookId: String) {
        ApiClient.instance.getBookDetail(bookId).enqueue(object : Callback<BookDetailResponse> {
            override fun onResponse(call: Call<BookDetailResponse>, response: Response<BookDetailResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val bookDetail = response.body()
                    updateUI(bookDetail)
                } else {
                    Toast.makeText(this@BookDetailActivity, "Ошибка загрузки данных о книге", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<BookDetailResponse>, t: Throwable) {
                Toast.makeText(this@BookDetailActivity, "Ошибка сети: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    /**
     * Обновляет UI с данными книги.
     */
    private fun updateUI(bookDetail: BookDetailResponse?) {
        if (bookDetail != null) {
            findViewById<TextView>(R.id.tvBookTitle)?.text = bookDetail.title ?: "Без названия"
            findViewById<TextView>(R.id.tvBookAuthor)?.text = bookDetail.authors ?: "Автор неизвестен"
            findViewById<TextView>(R.id.tvAnnotation)?.text = bookDetail.annotation ?: "Нет описания"

            // Устанавливаем прогресс в ProgressBar и TextView
            val progress = bookDetail.progress // Если сервер точно возвращает значение, это безопасно
            progressBar.progress = progress
            tvProgress.text = "$progress%"
            findViewById<TextView>(R.id.tvReadingStatus)?.text = bookDetail.status ?: "Статус неизвестен"
        } else {
            Toast.makeText(this, "Ошибка: данные книги отсутствуют", Toast.LENGTH_SHORT).show()
            finish()
        }
    }
}
