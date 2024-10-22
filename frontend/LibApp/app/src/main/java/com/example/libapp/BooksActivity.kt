package com.example.libapp

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.view.View
import android.widget.Button
import android.widget.ProgressBar
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.libapp.adapters.BooksAdapter
import com.example.libapp.api.ApiClient
import com.example.libapp.models.Book
import com.example.libapp.models.BookResponse
import com.example.libapp.models.UserBooksResponse
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File
import androidx.activity.enableEdgeToEdge

class BooksActivity : AppCompatActivity() {

    private lateinit var rvBooks: RecyclerView
    private lateinit var btnUploadBook: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var loadingOverlay: View
    private var userId: String? = null
    private val books = mutableListOf<Book>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_books)

        rvBooks = findViewById(R.id.rvBooks)
        btnUploadBook = findViewById(R.id.btnUploadBook)
        progressBar = findViewById(R.id.progressBar)
        loadingOverlay = findViewById(R.id.loadingOverlay)

        userId = intent.getStringExtra("USER_ID")

        rvBooks.layoutManager = LinearLayoutManager(this)
        rvBooks.adapter = BooksAdapter(books) { book ->
            openBookDetail(book)
        }

        btnUploadBook.setOnClickListener {
            openFilePicker()
        }

        loadBooks() // Загружаем книги при открытии экрана
    }

    /**
     * Показать индикатор загрузки с анимацией
     */
    private fun showLoading() {
        // Сначала убедимся, что ProgressBar и Overlay видимы и прозрачны
        progressBar.apply {
            alpha = 0f
            visibility = View.VISIBLE
            animate()
                .alpha(1f)
                .setDuration(300)
                .setListener(null)
        }

        loadingOverlay.apply {
            alpha = 0f
            visibility = View.VISIBLE
            animate()
                .alpha(1f)
                .setDuration(300)
                .setListener(null)
        }
    }

    /**
     * Скрыть индикатор загрузки с анимацией
     */
    private fun hideLoading() {
        progressBar.animate()
            .alpha(0f)
            .setDuration(300)
            .withEndAction {
                progressBar.visibility = View.GONE
            }

        loadingOverlay.animate()
            .alpha(0f)
            .setDuration(300)
            .withEndAction {
                loadingOverlay.visibility = View.GONE
            }
    }

    private fun loadBooks() {
        userId?.let { id ->
            showLoading() // Показываем индикатор загрузки

            ApiClient.instance.getUser(id).enqueue(object : Callback<UserBooksResponse> {
                override fun onResponse(call: Call<UserBooksResponse>, response: Response<UserBooksResponse>) {
                    hideLoading() // Скрываем индикатор загрузки

                    if (response.isSuccessful) {
                        response.body()?.let { userBooksResponse ->
                            books.clear()
                            books.addAll(userBooksResponse.books)
                            rvBooks.adapter?.notifyDataSetChanged()
                        }
                    } else {
                        Toast.makeText(this@BooksActivity, "Не удалось загрузить книги", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<UserBooksResponse>, t: Throwable) {
                    hideLoading() // Скрываем индикатор загрузки
                    Toast.makeText(this@BooksActivity, "Ошибка при загрузке книг: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }
    }

    private fun uploadBook(userId: String, fileUri: Uri) {
        showLoading() // Показываем индикатор загрузки

        val userIdBody = userId.toRequestBody("text/plain".toMediaTypeOrNull())
        val file = uriToFile(fileUri)
        val requestFile = file.asRequestBody("application/octet-stream".toMediaTypeOrNull())
        val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

        ApiClient.instance.uploadBook(userIdBody, filePart).enqueue(object : Callback<BookResponse> {
            override fun onResponse(call: Call<BookResponse>, response: Response<BookResponse>) {
                hideLoading() // Скрываем индикатор загрузки

                if (response.isSuccessful && response.body()?.status == "success") {
                    Toast.makeText(this@BooksActivity, "Книга успешно загружена", Toast.LENGTH_SHORT).show()

                    response.body()?.book?.let { uploadedBook ->
                        books.add(uploadedBook)
                        rvBooks.adapter?.notifyItemInserted(books.size - 1)
                    } ?: run {
                        Toast.makeText(this@BooksActivity, "Не удалось получить данные о загруженной книге", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    val message = response.body()?.message ?: "Неизвестная ошибка"
                    Toast.makeText(this@BooksActivity, "Ошибка загрузки: $message", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<BookResponse>, t: Throwable) {
                hideLoading() // Скрываем индикатор загрузки
                Toast.makeText(this@BooksActivity, "Ошибка: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun openFilePicker() {
        val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "*/*"
            addCategory(Intent.CATEGORY_OPENABLE)
        }
        filePickerLauncher.launch(intent)
    }

    private val filePickerLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == RESULT_OK) {
            result.data?.data?.let { uri ->
                userId?.let { id ->
                    uploadBook(id, uri)
                } ?: run {
                    Toast.makeText(this, "User ID is missing", Toast.LENGTH_SHORT).show()
                }
            }
        } else {
            Toast.makeText(this, "File selection cancelled", Toast.LENGTH_SHORT).show()
        }
    }

    private fun openBookDetail(book: Book) {
        val intent = Intent(this, BookAnnotationActivity::class.java)
        intent.putExtra("BOOK_ID", book.idBook)
        startActivity(intent)
    }

    private fun uriToFile(uri: Uri): File {
        val fileName = getFileName(uri)
        val tempFile = File.createTempFile("upload_", fileName, cacheDir)
        tempFile.outputStream().use { outputStream ->
            contentResolver.openInputStream(uri)?.use { inputStream ->
                inputStream.copyTo(outputStream)
            }
        }
        return tempFile
    }

    private fun getFileName(uri: Uri): String {
        var name = "file"
        val cursor = contentResolver.query(uri, null, null, null, null)
        cursor?.use {
            val nameIndex = it.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (nameIndex != -1 && it.moveToFirst()) {
                name = it.getString(nameIndex)
            }
        }
        return name
    }
}
