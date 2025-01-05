package com.example.libapp

import android.os.Bundle
import android.view.View
import android.widget.ImageButton
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.viewpager2.widget.ViewPager2
import com.example.libapp.adapters.PageAdapter
import com.example.libapp.api.ApiClient
import com.example.libapp.models.BookDetailResponse
import com.example.libapp.models.CompressionResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class BookReadingActivity : AppCompatActivity() {

    private lateinit var viewPager: ViewPager2
    private lateinit var tvPageIndicator: TextView
    private lateinit var progressBar: ProgressBar

    private var bookId: String? = null
    private var totalPages: Int = 0
    private val pages: MutableList<String> = mutableListOf()

    private var compressionLevel: Int = 0 // Уровень сжатия: 0 - оригинальный текст

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_book_reading)

        viewPager = findViewById(R.id.viewPager)
        tvPageIndicator = findViewById(R.id.tvPageIndicator)
        progressBar = findViewById(R.id.progressBar)

        bookId = intent.getStringExtra("BOOK_ID")
        compressionLevel = intent.getIntExtra("COMPRESSION_LEVEL", 0)

        // Проверка на наличие `COMPRESSED_CONTENT` из Intent
        val compressedContent = intent.getStringExtra("COMPRESSED_CONTENT")

        // Обработка нажатия на кнопку "Назад"
        findViewById<ImageButton>(R.id.btnBack)?.setOnClickListener {
            finish() // Закрывает текущую Activity и возвращается к предыдущей
        }

        if (bookId != null) {
            showLoading() // Показываем загрузку при переходе
            if (!compressedContent.isNullOrEmpty()) {
                // Загружаем сжатый текст из Intent
                loadCompressedContentFromIntent(compressedContent)
            } else {
                // Загружаем данные с сервера
                loadContent(bookId!!)
            }
        } else {
            Toast.makeText(this, "Ошибка: ID книги не предоставлен.", Toast.LENGTH_SHORT).show()
            finish()
        }

        viewPager.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
            override fun onPageSelected(position: Int) {
                super.onPageSelected(position)
                tvPageIndicator.text = "${position + 1}/$totalPages"
            }
        })
    }

    /**
     * Загружает данные книги с учетом уровня сжатия.
     */
    private fun loadContent(bookId: String) {
        if (compressionLevel == 0) {
            // Загружаем оригинальные текстовые блоки
            fetchOriginalText(bookId)
        } else {
            // Загружаем сжатые текстовые блоки с сервера
            fetchCompressedText(bookId, compressionLevel)
        }
    }

    /**
     * Загружает сжатый текст из Intent.
     */
    private fun loadCompressedContentFromIntent(compressedContent: String) {
        pages.clear()
        val compressedBlocks = compressedContent.split("\n") // Разделяем текст на страницы
        pages.addAll(compressedBlocks)
        totalPages = pages.size
        setupViewPager()
    }

    /**
     * Загружает оригинальные текстовые блоки книги.
     */
    private fun fetchOriginalText(bookId: String) {
        ApiClient.instance.getBookDetail(bookId).enqueue(object : Callback<BookDetailResponse> {
            override fun onResponse(call: Call<BookDetailResponse>, response: Response<BookDetailResponse>) {
                if (response.isSuccessful) {
                    response.body()?.let { bookDetail ->
                        totalPages = bookDetail.totalPages
                        pages.clear()
                        pages.addAll(bookDetail.textBlocks)
                        setupViewPager()
                    } ?: run {
                        hideLoading()
                        Toast.makeText(this@BookReadingActivity, "Не удалось получить данные о книге.", Toast.LENGTH_SHORT).show()
                        finish()
                    }
                } else {
                    hideLoading()
                    Toast.makeText(this@BookReadingActivity, "Ошибка: ${response.message()}", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }

            override fun onFailure(call: Call<BookDetailResponse>, t: Throwable) {
                hideLoading()
                Toast.makeText(this@BookReadingActivity, "Ошибка сети: ${t.message}", Toast.LENGTH_SHORT).show()
                finish()
            }
        })
    }

    /**
     * Загружает сжатые текстовые блоки книги.
     */
    private fun fetchCompressedText(bookId: String, compressionLevel: Int) {
        ApiClient.instance.compressBook(bookId, compressionLevel).enqueue(object : Callback<CompressionResponse> {
            override fun onResponse(call: Call<CompressionResponse>, response: Response<CompressionResponse>) {
                if (response.isSuccessful) {
                    response.body()?.let { compressionResponse ->
                        pages.clear()
                        pages.addAll(compressionResponse.pages) // Используем массив страниц
                        totalPages = pages.size
                        setupViewPager()
                    } ?: run {
                        hideLoading()
                        Toast.makeText(this@BookReadingActivity, "Ошибка при загрузке сжатого текста.", Toast.LENGTH_SHORT).show()
                        finish()
                    }
                } else {
                    hideLoading()
                    Toast.makeText(this@BookReadingActivity, "Ошибка: ${response.message()}", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }

            override fun onFailure(call: Call<CompressionResponse>, t: Throwable) {
                hideLoading()
                Toast.makeText(this@BookReadingActivity, "Ошибка сети: ${t.message}", Toast.LENGTH_SHORT).show()
                finish()
            }
        })
    }

    /**
     * Настраивает ViewPager для отображения страниц.
     */
    private fun setupViewPager() {
        val pageAdapter = PageAdapter(pages)
        viewPager.adapter = pageAdapter
        tvPageIndicator.text = "1/$totalPages"
        hideLoading()
    }

    /**
     * Показывает индикатор загрузки.
     */
    private fun showLoading() {
        progressBar.visibility = View.VISIBLE
        viewPager.visibility = View.GONE
        tvPageIndicator.visibility = View.GONE
    }

    /**
     * Скрывает индикатор загрузки.
     */
    private fun hideLoading() {
        progressBar.visibility = View.GONE
        viewPager.visibility = View.VISIBLE
        tvPageIndicator.visibility = View.VISIBLE
    }
}
