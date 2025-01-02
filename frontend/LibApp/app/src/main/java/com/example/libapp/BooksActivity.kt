package com.example.libapp

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.util.Log
import android.view.View
import android.widget.ImageButton
import android.widget.ProgressBar
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.libapp.adapters.BookAdapter
import com.example.libapp.api.ApiClient
import com.example.libapp.models.BookResponse
import com.example.libapp.viewmodels.BookViewModel
import com.google.android.material.bottomnavigation.BottomNavigationView
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File

class BooksActivity : AppCompatActivity() {

    private lateinit var bottomNavigationView: BottomNavigationView
    private lateinit var allBooksButton: ImageButton
    private lateinit var addButton: ImageButton
    private lateinit var recyclerView: RecyclerView
    private lateinit var bookAdapter: BookAdapter
    private lateinit var progressBar: ProgressBar

    private val bookViewModel: BookViewModel by viewModels()

    private val filePickerLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == RESULT_OK) {
                val uri: Uri? = result.data?.data
                val userId = intent.getStringExtra("USER_ID") ?: return@registerForActivityResult
                if (uri != null) {
                    uploadFile(userId, uri)
                } else {
                    Toast.makeText(this, "Файл не выбран", Toast.LENGTH_SHORT).show()
                }
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_books)

        allBooksButton = findViewById(R.id.adjustable_btn)
        addButton = findViewById(R.id.btnAdd)
        recyclerView = findViewById(R.id.rvBooks)
        bottomNavigationView = findViewById(R.id.bottomNavigationView)
        progressBar = findViewById(R.id.progressBar)

        recyclerView.layoutManager = LinearLayoutManager(this)
        bookAdapter = BookAdapter(emptyList()) { book ->
            val intent = Intent(this, BookDetailActivity::class.java)
            intent.putExtra("BOOK_ID", book.idBook)
            startActivity(intent)
        }
        recyclerView.adapter = bookAdapter

        val userId = intent.getStringExtra("USER_ID") ?: run {
            Toast.makeText(this, "Ошибка: не удалось получить ID пользователя", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        bookViewModel.books.observe(this) { books ->
            hideLoading()
            bookAdapter.updateBooks(books)
        }

        bookViewModel.error.observe(this) { errorMessage ->
            hideLoading()
            Toast.makeText(this, "Ошибка загрузки книг: $errorMessage", Toast.LENGTH_SHORT).show()
        }

        loadBooks(userId)

        allBooksButton.setOnClickListener {
            loadBooks(userId)
        }

        addButton.setOnClickListener {
            openFilePicker()
        }

        //        favoriteBooksButton.setOnClickListener {
//            updateButtonStyles(isAllSelected = false)
//            showLoading() // Показываем ProgressBar при загрузке избранных книг
//            bookViewModel.loadFavoriteBooks() // Загрузка избранных книг
//        }

        // Настройка нижнего меню
        bottomNavigationView.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.menu_books -> true // Текущий экран
//                R.id.menu_search -> {
//                    startActivity(Intent(this, SearchActivity::class.java))
//                    finish()
//                    true
//                }
//                R.id.menu_chat -> {
//                    startActivity(Intent(this, ChatActivity::class.java))
//                    finish()
//                    true
//                }
//                R.id.menu_profile -> {
//                    startActivity(Intent(this, ProfileActivity::class.java))
//                    finish()
//                    true
//                }
                else -> false
            }
        }

        bottomNavigationView.selectedItemId = R.id.menu_books
    }

    private fun loadBooks(userId: String) {
        showLoading()
        bookViewModel.loadUserBooks(userId)
    }

    private fun openFilePicker() {
        val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "*/*"
            addCategory(Intent.CATEGORY_OPENABLE)
        }
        filePickerLauncher.launch(intent)
    }

    private fun uploadFile(userId: String, fileUri: Uri) {
        showLoading()

        val file = uriToFile(fileUri)

        if (!file.exists()) {
            Log.e("BooksActivity", "Файл не существует: ${file.absolutePath}")
            Toast.makeText(this, "Ошибка: файл не найден", Toast.LENGTH_SHORT).show()
            hideLoading()
            return
        }

        val mimeType = contentResolver.getType(fileUri) ?: "application/octet-stream"
        val requestFile = file.asRequestBody(mimeType.toMediaTypeOrNull())
        val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

        ApiClient.instance.uploadBook(userId, filePart).enqueue(object : Callback<BookResponse> {
            override fun onResponse(call: Call<BookResponse>, response: Response<BookResponse>) {
                hideLoading()
                if (response.isSuccessful && response.body()?.status == "success") {
                    Toast.makeText(this@BooksActivity, "Файл успешно загружен!", Toast.LENGTH_SHORT).show()
                    loadBooks(userId)
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Неизвестная ошибка"
                    Toast.makeText(this@BooksActivity, "Ошибка загрузки файла: $errorBody", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<BookResponse>, t: Throwable) {
                hideLoading()
                Toast.makeText(this@BooksActivity, "Не удалось загрузить файл", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun uriToFile(uri: Uri): File {
        val fileName = getFileName(uri)
        val tempFile = File(cacheDir, fileName)
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

    private fun showLoading() {
        progressBar.visibility = View.VISIBLE
    }

    private fun hideLoading() {
        progressBar.visibility = View.GONE
    }
}
