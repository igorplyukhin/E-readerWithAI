package com.example.libapp

import android.content.Intent
import android.os.Bundle
import android.view.View
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
    private lateinit var fullScreenLoader: View // Поле для полноэкранного индикатора загрузки
    private lateinit var loaderProgressBar: ProgressBar // Прогресс-бар загрузки
    private lateinit var btnReadBook: Button // Кнопка "Читать книгу"
    private lateinit var btnCompressText: Button // Кнопка "Сжать текст"
    private lateinit var btnBack: ImageButton // Кнопка "Назад"
    private var bookId: String? = null // Хранение bookId
    private var compressionLevel: Int = 0 // Текущий уровень сжатия

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_book_detail)

        // Инициализация элементов интерфейса
        progressBar = findViewById(R.id.progressBar)
        tvProgress = findViewById(R.id.tvProgress)
        fullScreenLoader = findViewById(R.id.fullScreenLoader) // Инициализация полноэкранного индикатора
        loaderProgressBar = findViewById(R.id.loaderProgressBar) // Инициализация прогресс-бара
        btnReadBook = findViewById(R.id.btnReadBook)
        btnCompressText = findViewById(R.id.btnCompressText)
        btnBack = findViewById(R.id.btnBack)

        // Обработка нажатия на кнопку "Назад"
        btnBack.setOnClickListener {
            finish() // Закрывает текущую Activity и возвращается к предыдущей
        }

        // Получение bookId из Intent
        bookId = intent.getStringExtra("BOOK_ID")
        if (bookId != null) {
            showLoading() // Показываем индикатор загрузки
            setEnabledState(false) // Отключаем кнопки во время загрузки
            loadBookDetails(bookId!!)
        } else {
            Toast.makeText(this, "Ошибка: книга не найдена", Toast.LENGTH_SHORT).show()
            finish()
        }

        // Обработка нажатия на кнопку "Читать книгу"
        btnReadBook.setOnClickListener {
            if (bookId != null) {
                // Переход к BookReadingActivity с передачей bookId
                val intent = Intent(this, BookReadingActivity::class.java)
                intent.putExtra("BOOK_ID", bookId)
                startActivity(intent)
            } else {
                Toast.makeText(this, "Ошибка: ID книги отсутствует", Toast.LENGTH_SHORT).show()
            }
        }

        // Обработка нажатия на кнопку "Сжать текст"
        btnCompressText.setOnClickListener {
            val bottomSheet = BottomSheetCompress()
            bottomSheet.setCurrentCompressionLevel(compressionLevel) // Передаем текущее значение
            bottomSheet.setOnApplyClickListener { selectedCompressionLevel ->
                updateCompressionLevel(selectedCompressionLevel) // Обновляем уровень сжатия
            }
            bottomSheet.show(supportFragmentManager, "BottomSheetCompress")
        }
    }

    /**
     * Загружает информацию о книге с указанным ID с сервера.
     */
    private fun loadBookDetails(bookId: String) {
        ApiClient.instance.getBookDetail(bookId).enqueue(object : Callback<BookDetailResponse> {
            override fun onResponse(call: Call<BookDetailResponse>, response: Response<BookDetailResponse>) {
                hideLoading() // Скрываем индикатор загрузки
                setEnabledState(true) // Включаем кнопки после загрузки
                if (response.isSuccessful && response.body() != null) {
                    val bookDetail = response.body()
                    updateUI(bookDetail)
                } else {
                    Toast.makeText(this@BookDetailActivity, "Ошибка загрузки данных о книге", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<BookDetailResponse>, t: Throwable) {
                hideLoading() // Скрываем индикатор загрузки
                setEnabledState(true) // Включаем кнопки после ошибки
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

            // Устанавливаем уровень сжатия
            compressionLevel = bookDetail.compressionLevel // Поле compressionLevel
        } else {
            Toast.makeText(this, "Ошибка: данные книги отсутствуют", Toast.LENGTH_SHORT).show()
            finish()
        }
    }

    /**
     * Обновляет уровень сжатия книги на сервере.
     */
    private fun updateCompressionLevel(newCompressionLevel: Int) {
        if (bookId == null) {
            Toast.makeText(this, "Ошибка: ID книги отсутствует", Toast.LENGTH_SHORT).show()
            return
        }

        val data = mapOf("compressionLevel" to newCompressionLevel)

        ApiClient.instance.updateBookCompressionLevel(bookId!!, data).enqueue(object : Callback<Void> {
            override fun onResponse(call: Call<Void>, response: Response<Void>) {
                if (response.isSuccessful) {
                    compressionLevel = newCompressionLevel
                    Toast.makeText(this@BookDetailActivity, "Уровень сжатия обновлен", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this@BookDetailActivity, "Ошибка обновления уровня сжатия", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<Void>, t: Throwable) {
                Toast.makeText(this@BookDetailActivity, "Ошибка сети при обновлении уровня сжатия: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    /**
     * Показывает индикатор загрузки.
     */
    private fun showLoading() {
        fullScreenLoader.visibility = View.VISIBLE
        loaderProgressBar.visibility = View.VISIBLE
    }

    /**
     * Скрывает индикатор загрузки.
     */
    private fun hideLoading() {
        fullScreenLoader.visibility = View.GONE
        loaderProgressBar.visibility = View.GONE
    }

    /**
     * Включает или отключает элементы интерфейса.
     */
    private fun setEnabledState(enabled: Boolean) {
        btnReadBook.isEnabled = enabled
        btnCompressText.isEnabled = enabled
        btnBack.isEnabled = enabled
    }
}
