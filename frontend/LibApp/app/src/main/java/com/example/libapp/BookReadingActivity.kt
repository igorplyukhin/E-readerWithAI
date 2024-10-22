package com.example.libapp

import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.viewpager2.widget.ViewPager2
import com.example.libapp.adapters.PageAdapter
import com.example.libapp.api.ApiClient
import com.example.libapp.models.BookDetailResponse
import com.example.libapp.models.BookPageResponse
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

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_book_reading)

        viewPager = findViewById(R.id.viewPager)
        tvPageIndicator = findViewById(R.id.tvPageIndicator)
        progressBar = findViewById(R.id.progressBar)

        bookId = intent.getStringExtra("BOOK_ID")

        if (bookId != null) {
            showLoading() // Показываем загрузку при переходе
            fetchTotalPages(bookId!!)
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

    private fun fetchTotalPages(bookId: String) {
        ApiClient.instance.getBookDetail(bookId).enqueue(object : Callback<BookDetailResponse> {
            override fun onResponse(call: Call<BookDetailResponse>, response: Response<BookDetailResponse>) {
                if (response.isSuccessful) {
                    response.body()?.let { bookDetail ->
                        totalPages = bookDetail.totalPages
                        setupViewPager(bookId)
                        tvPageIndicator.text = "1/$totalPages"  // Устанавливаем индикатор страниц сразу после получения данных
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

    private fun setupViewPager(bookId: String) {
        val pageAdapter = PageAdapter(pages)
        viewPager.adapter = pageAdapter
        fetchPage(bookId, 1)
    }

    private fun fetchPage(bookId: String, pageNumber: Int) {
        ApiClient.instance.getBookPage(bookId, pageNumber).enqueue(object : Callback<BookPageResponse> {
            override fun onResponse(call: Call<BookPageResponse>, response: Response<BookPageResponse>) {
                if (response.isSuccessful) {
                    response.body()?.let { pageResponse ->
                        pages.add(pageResponse.content)

                        if (pageResponse.pageNumber == 1) {
                            // Скрываем загрузку после загрузки первой страницы
                            hideLoading()
                            viewPager.adapter?.notifyDataSetChanged()
                        } else {
                            // Обновляем адаптер для последующих страниц
                            viewPager.adapter?.notifyItemInserted(pages.size - 1)
                        }

                        if (pageResponse.pageNumber < totalPages) {
                            fetchPage(bookId, pageResponse.pageNumber + 1)
                        }
                    }
                } else {
                    hideLoading()
                    Toast.makeText(this@BookReadingActivity, "Ошибка при загрузке страницы $pageNumber: ${response.message()}", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<BookPageResponse>, t: Throwable) {
                hideLoading()
                Toast.makeText(this@BookReadingActivity, "Ошибка сети при загрузке страницы $pageNumber: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    // Показываем прогресс бар
    private fun showLoading() {
        progressBar.visibility = View.VISIBLE
        viewPager.visibility = View.GONE
    }

    // Скрываем прогресс бар
    private fun hideLoading() {
        progressBar.visibility = View.GONE
        viewPager.visibility = View.VISIBLE
    }
}




