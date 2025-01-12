package com.example.libapp

import android.os.Bundle
import android.util.Log
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
    private lateinit var pageAdapter: PageAdapter

    private var bookId: String? = null
    private var totalPages: Int = 0
    private val pages: MutableList<String> = mutableListOf()

    private var compressionLevel: Int = 0
    private var lastReadPage: Int = 0 //

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_book_reading)

        viewPager = findViewById(R.id.viewPager)
        tvPageIndicator = findViewById(R.id.tvPageIndicator)
        progressBar = findViewById(R.id.progressBar)

        bookId = intent.getStringExtra("BOOK_ID")
        compressionLevel = intent.getIntExtra("COMPRESSION_LEVEL", 0)
        lastReadPage = intent.getIntExtra("LAST_READ_PAGE", 0)

        val compressedContent = intent.getStringExtra("COMPRESSED_CONTENT")

        findViewById<ImageButton>(R.id.btnBack)?.setOnClickListener {
            finish()
        }

        if (bookId != null) {
            showLoading()
            Log.d("BookReadingActivity", "Book ID: $bookId, Compression Level: $compressionLevel")
            if (!compressedContent.isNullOrEmpty()) {
                Log.d("BookReadingActivity", "Compressed content detected in intent.")
                loadCompressedContentFromIntent(compressedContent)
            } else {
                Log.d("BookReadingActivity", "No compressed content in intent. Loading content from server.")
                loadContent(bookId!!)
            }
        } else {
            Log.e("BookReadingActivity", "Error: Book ID not provided.")
            Toast.makeText(this, "Ошибка: ID книги не предоставлен.", Toast.LENGTH_SHORT).show()
            finish()
        }

        viewPager.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
            override fun onPageSelected(position: Int) {
                super.onPageSelected(position)
                tvPageIndicator.text = "${position + 1}/$totalPages"
                Log.d("BookReadingActivity", "Page selected: ${position + 1}")
                updateProgressOnServer(position)
                lastReadPage = position
            }
        })
    }

    override fun onResume() {
        super.onResume()
        if (bookId != null) {
            Log.d("BookReadingActivity", "Resuming activity. Reloading content for book ID: $bookId")
            loadContent(bookId!!)
        }
    }

    private fun loadContent(bookId: String) {
        if (pages.isNotEmpty()) {
            Log.d("BookReadingActivity", "Pages already loaded. Setting up ViewPager.")
            setupViewPager()
        } else {
            if (compressionLevel == 0) {
                Log.d("BookReadingActivity", "Fetching original text for book ID: $bookId")
                fetchOriginalText(bookId)
            } else {
                Log.d("BookReadingActivity", "Fetching compressed text for book ID: $bookId with compression level: $compressionLevel")
                fetchCompressedText(bookId, compressionLevel)
            }
        }
    }

    private fun loadCompressedContentFromIntent(compressedContent: String) {
        Log.d("BookReadingActivity", "Processing compressed content from intent.")
        pages.clear()
        val compressedBlocks = compressedContent.split("\n")
        Log.d("BookReadingActivity", "Compressed content contains ${compressedBlocks.size} blocks.")
        pages.addAll(compressedBlocks)
        totalPages = pages.size
        setupViewPager()
        moveToLastReadPage()
    }

    private fun fetchOriginalText(bookId: String) {
        ApiClient.instance.getBookDetail(bookId).enqueue(object : Callback<BookDetailResponse> {
            override fun onResponse(call: Call<BookDetailResponse>, response: Response<BookDetailResponse>) {
                if (response.isSuccessful) {
                    response.body()?.let { bookDetail ->
                        Log.d("BookReadingActivity", "Original text loaded. Total pages: ${bookDetail.totalPages}")
                        totalPages = bookDetail.totalPages
                        pages.clear()
                        pages.addAll(bookDetail.textBlocks)
                        lastReadPage = bookDetail.blockStopBook
                        setupViewPager()
                        moveToLastReadPage()
                    } ?: run {
                        Log.e("BookReadingActivity", "Failed to parse book detail response.")
                        hideLoading()
                        Toast.makeText(this@BookReadingActivity, "Не удалось получить данные о книге.", Toast.LENGTH_SHORT).show()
                        finish()
                    }
                } else {
                    Log.e("BookReadingActivity", "Failed to load original text. Error: ${response.message()}")
                    hideLoading()
                    Toast.makeText(this@BookReadingActivity, "Ошибка: ${response.message()}", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }

            override fun onFailure(call: Call<BookDetailResponse>, t: Throwable) {
                Log.e("BookReadingActivity", "Network error while loading original text: ${t.message}")
                hideLoading()
                Toast.makeText(this@BookReadingActivity, "Ошибка сети: ${t.message}", Toast.LENGTH_SHORT).show()
                t.printStackTrace()
                finish()
            }
        })
    }

    private fun fetchCompressedText(bookId: String, compressionLevel: Int) {
        ApiClient.instance.compressBook(bookId, compressionLevel).enqueue(object : Callback<CompressionResponse> {
            override fun onResponse(call: Call<CompressionResponse>, response: Response<CompressionResponse>) {
                if (response.isSuccessful) {
                    response.body()?.let { compressionResponse ->
                        Log.d("BookReadingActivity", "Compressed text loaded. Total compressed pages: ${compressionResponse.pages.size}")
                        pages.clear()
                        pages.addAll(compressionResponse.pages)
                        totalPages = pages.size
                        setupViewPager()
                        moveToLastReadPage()
                    } ?: run {
                        Log.e("BookReadingActivity", "Failed to parse compression response.")
                        hideLoading()
                        Toast.makeText(this@BookReadingActivity, "Ошибка при загрузке сжатого текста.", Toast.LENGTH_SHORT).show()
                        finish()
                    }
                } else {
                    Log.e("BookReadingActivity", "Failed to load compressed text. Error: ${response.message()}")
                    hideLoading()
                    Toast.makeText(this@BookReadingActivity, "Ошибка: ${response.message()}", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }

            override fun onFailure(call: Call<CompressionResponse>, t: Throwable) {
                Log.e("BookReadingActivity", "Network error while loading compressed text: ${t.message}")
                hideLoading()
                Toast.makeText(this@BookReadingActivity, "Ошибка сети: ${t.message}", Toast.LENGTH_SHORT).show()
                t.printStackTrace()
                finish()
            }
        })
    }

    private fun setupViewPager() {
        if (pages.isEmpty()) {
            Log.e("BookReadingActivity", "No pages to display. Exiting.")
            Toast.makeText(this, "Книга пуста или данные не загружены.", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        Log.d("BookReadingActivity", "Setting up ViewPager with $totalPages pages.")
        pageAdapter = PageAdapter(pages)
        viewPager.adapter = pageAdapter
        hideLoading()
    }

    private fun moveToLastReadPage() {
        if (lastReadPage in 0 until totalPages) {
            Log.d("BookReadingActivity", "Moving to last read page: ${lastReadPage + 1}")
            viewPager.setCurrentItem(lastReadPage, false)
            tvPageIndicator.text = "${lastReadPage + 1}/$totalPages"
        } else {
            Log.d("BookReadingActivity", "Last read page is out of bounds. Skipping move.")
        }
    }

    private fun updateProgressOnServer(blockIndex: Int) {
        bookId?.let { id ->
            ApiClient.instance.updateBookProgress(id, blockIndex, totalPages).enqueue(object : Callback<Map<String, Int>> {
                override fun onResponse(call: Call<Map<String, Int>>, response: Response<Map<String, Int>>) {
                    if (response.isSuccessful) {
                        val progressData = response.body()
                        progressData?.let {
                            val updatedProgress = it["progress"] ?: 0
                            Log.d("BookReadingActivity", "Progress updated on server: $updatedProgress% (page: ${blockIndex + 1})")

                            lastReadPage = blockIndex
                            Log.d("BookReadingActivity", "Updated lastReadPage to: $lastReadPage")
                        }
                    } else {
                        Log.e("BookReadingActivity", "Failed to update progress. Error: ${response.message()}")
                        Toast.makeText(this@BookReadingActivity, "Ошибка обновления прогресса.", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<Map<String, Int>>, t: Throwable) {
                    Log.e("BookReadingActivity", "Network error while updating progress: ${t.message}")
                    Toast.makeText(this@BookReadingActivity, "Ошибка сети: ${t.message}", Toast.LENGTH_SHORT).show()
                    t.printStackTrace()
                }
            })
        }
    }

    private fun showLoading() {
        Log.d("BookReadingActivity", "Showing loading indicator")
        progressBar.visibility = View.VISIBLE
        viewPager.visibility = View.GONE
        tvPageIndicator.visibility = View.GONE
    }

    private fun hideLoading() {
        Log.d("BookReadingActivity", "Hiding loading indicator")
        progressBar.visibility = View.GONE
        viewPager.visibility = View.VISIBLE
        tvPageIndicator.visibility = View.VISIBLE
    }
}
