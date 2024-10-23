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
import android.os.Handler
import android.os.Looper
import android.util.Log

class BookReadingActivity : AppCompatActivity() {

    private lateinit var viewPager: ViewPager2
    private lateinit var tvPageIndicator: TextView
    private lateinit var progressBar: ProgressBar

    private var bookId: String? = null
    private var totalPages: Int = 0
    private val pages: MutableList<String> = mutableListOf()

    private var sessionReadingTime: Long = 0
    private var totalReadingTime: Long = 0
    private var startTime: Long = 0

    private val handler = Handler(Looper.getMainLooper())
    private val updateReadingTimeRunnable = object : Runnable {
        override fun run() {
            if (startTime != 0L) {
                sessionReadingTime += 5000 // Инкрементируем на 5 секунд
                totalReadingTime += 5000
                Log.d("BookReadingActivity", "Session Reading Time: $sessionReadingTime ms")
                Log.d("BookReadingActivity", "Total Reading Time: $totalReadingTime ms")
                Log.d("BookReadingActivity", "Session: $sessionReadingTime ms, Total: $totalReadingTime ms")
            }
            handler.postDelayed(this, 5000) // Обновляем каждые 5 секунд
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_book_reading)

        viewPager = findViewById(R.id.viewPager)
        tvPageIndicator = findViewById(R.id.tvPageIndicator)
        progressBar = findViewById(R.id.progressBar)

        bookId = intent.getStringExtra("BOOK_ID")

        if (bookId != null) {
            Log.d("BookReadingActivity", "Book ID: $bookId")
            showLoading()
            fetchTotalPages(bookId!!)
        } else {
            Log.e("BookReadingActivity", "Ошибка: ID книги не предоставлен.")
            Toast.makeText(this, "Ошибка: ID книги не предоставлен.", Toast.LENGTH_SHORT).show()
            finish()
        }

        viewPager.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
            override fun onPageSelected(position: Int) {
                super.onPageSelected(position)
                tvPageIndicator.text = "${position + 1}/$totalPages"
                Log.d("BookReadingActivity", "Page Selected: ${position + 1}")
                Log.d("BookReadingActivity", "Session Reading Time before reset: $sessionReadingTime ms")
                resetSessionReadingTime()
            }
        })
    }

    override fun onResume() {
        super.onResume()
        Log.d("BookReadingActivity", "Activity Resumed")
        startTiming()
    }

    override fun onPause() {
        super.onPause()
        Log.d("BookReadingActivity", "Activity Paused")
        stopTiming()
    }

    private fun startTiming() {
        startTime = System.currentTimeMillis()
        handler.post(updateReadingTimeRunnable)
    }

    private fun stopTiming() {
        handler.removeCallbacks(updateReadingTimeRunnable)
        startTime = 0
    }

    private fun resetSessionReadingTime() {
        sessionReadingTime = 0
        Log.d("BookReadingActivity", "Session Reading Time Reset")
    }

    private fun fetchTotalPages(bookId: String) {
        Log.d("BookReadingActivity", "Fetching total pages for book ID: $bookId")
        ApiClient.instance.getBookDetail(bookId).enqueue(object : Callback<BookDetailResponse> {
            override fun onResponse(call: Call<BookDetailResponse>, response: Response<BookDetailResponse>) {
                if (response.isSuccessful) {
                    response.body()?.let { bookDetail ->
                        totalPages = bookDetail.totalPages
                        Log.d("BookReadingActivity", "Total Pages: $totalPages")
                        setupViewPager(bookId)
                        tvPageIndicator.text = "1/$totalPages"
                    } ?: run {
                        hideLoading()
                        Log.e("BookReadingActivity", "Failed to get book details.")
                        Toast.makeText(this@BookReadingActivity, "Не удалось получить данные о книге.", Toast.LENGTH_SHORT).show()
                        finish()
                    }
                } else {
                    hideLoading()
                    Log.e("BookReadingActivity", "Error: ${response.message()}")
                    Toast.makeText(this@BookReadingActivity, "Ошибка: ${response.message()}", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }

            override fun onFailure(call: Call<BookDetailResponse>, t: Throwable) {
                hideLoading()
                Log.e("BookReadingActivity", "Network error: ${t.message}")
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
        Log.d("BookReadingActivity", "Fetching page $pageNumber for book ID: $bookId")
        ApiClient.instance.getBookPage(bookId, pageNumber).enqueue(object : Callback<BookPageResponse> {
            override fun onResponse(call: Call<BookPageResponse>, response: Response<BookPageResponse>) {
                if (response.isSuccessful) {
                    response.body()?.let { pageResponse ->
                        pages.add(pageResponse.content)
                        Log.d("BookReadingActivity", "Page ${pageResponse.pageNumber} loaded")

                        if (pageResponse.pageNumber == 1) {
                            hideLoading()
                            viewPager.adapter?.notifyDataSetChanged()
                        } else {
                            viewPager.adapter?.notifyItemInserted(pages.size - 1)
                        }

                        if (pageResponse.pageNumber < totalPages) {
                            fetchPage(bookId, pageResponse.pageNumber + 1)
                        }
                    }
                } else {
                    hideLoading()
                    Log.e("BookReadingActivity", "Error loading page $pageNumber: ${response.message()}")
                    Toast.makeText(this@BookReadingActivity, "Ошибка при загрузке страницы $pageNumber: ${response.message()}", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<BookPageResponse>, t: Throwable) {
                hideLoading()
                Log.e("BookReadingActivity", "Network error loading page $pageNumber: ${t.message}")
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





