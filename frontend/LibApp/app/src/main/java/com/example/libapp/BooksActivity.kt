package com.example.libapp

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.util.Log
import android.widget.ImageButton
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Observer
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
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File

class BooksActivity : AppCompatActivity() {

    private lateinit var bottomNavigationView: BottomNavigationView
    private lateinit var allBooksButton: ImageButton
    private lateinit var favoriteBooksButton: ImageButton
    private lateinit var addButton: ImageButton
    private lateinit var recyclerView: RecyclerView
    private lateinit var bookAdapter: BookAdapter

    // ViewModel для работы с книгами
    private val bookViewModel: BookViewModel by viewModels()

    // Callback для обработки результата выбора файла
    private val filePickerLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == RESULT_OK) {
                val uri: Uri? = result.data?.data
                if (uri != null) {
                    val userId = intent.getStringExtra("USER_ID") ?: return@registerForActivityResult
                    uploadFile(userId, uri)
                } else {
                    Toast.makeText(this, "Файл не выбран", Toast.LENGTH_SHORT).show()
                }
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_books)

        // Инициализация элементов интерфейса
        allBooksButton = findViewById(R.id.adjustable_btn)
        favoriteBooksButton = findViewById(R.id.old_btn)
        addButton = findViewById(R.id.btnAdd)
        recyclerView = findViewById(R.id.rvBooks)
        bottomNavigationView = findViewById(R.id.bottomNavigationView)

        // Настройка RecyclerView
        recyclerView.layoutManager = LinearLayoutManager(this)
        bookAdapter = BookAdapter(emptyList())
        recyclerView.adapter = bookAdapter

        // Установка начального состояния кнопок
        updateButtonStyles(isAllSelected = true)

        // Загрузка всех книг по умолчанию
        bookViewModel.loadAllBooks()

        // Наблюдение за изменениями списка книг
        bookViewModel.books.observe(this, Observer { books ->
            Log.d("BooksActivity", "Получено книг для отображения: ${books.size}")
            bookAdapter.updateBooks(books)
        })

        // Обработка нажатий на кнопки "Все" и "Избранное"
        allBooksButton.setOnClickListener {
            updateButtonStyles(isAllSelected = true)
            bookViewModel.loadAllBooks()
        }

        favoriteBooksButton.setOnClickListener {
            updateButtonStyles(isAllSelected = false)
            bookViewModel.loadFavoriteBooks()
        }

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

        // Установка выделенного пункта меню
        bottomNavigationView.selectedItemId = R.id.menu_books

        // Обработка нажатия на кнопку "Добавить файл"
        addButton.setOnClickListener {
            openFilePicker()
        }
    }

    /**
     * Открывает проводник для выбора файла.
     */
    private fun openFilePicker() {
        val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "*/*"
            addCategory(Intent.CATEGORY_OPENABLE)
        }
        filePickerLauncher.launch(intent)
    }

    /**
     * Загружает файл на сервер.
     *
     * @param userId - ID пользователя.
     * @param fileUri - URI выбранного файла.
     */
    private fun uploadFile(userId: String, fileUri: Uri) {
        val file = uriToFile(fileUri)

        if (!file.exists()) {
            Log.e("BooksActivity", "Файл не существует: ${file.absolutePath}")
            Toast.makeText(this, "Ошибка: файл не найден", Toast.LENGTH_SHORT).show()
            return
        }

        // Поле id (как Form на сервере)
        val userIdPart = userId.toRequestBody("text/plain".toMediaTypeOrNull())

        // MIME-тип файла
        val mimeType = contentResolver.getType(fileUri) ?: "application/octet-stream"
        val requestFile = file.asRequestBody(mimeType.toMediaTypeOrNull())

        // Файл (как File на сервере)
        val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

        Log.d("BooksActivity", "Загрузка файла: ${file.name}, MIME-тип: $mimeType")

        ApiClient.instance.uploadBook(userIdPart, filePart).enqueue(object : Callback<BookResponse> {
            override fun onResponse(call: Call<BookResponse>, response: Response<BookResponse>) {
                if (response.isSuccessful) {
                    Toast.makeText(this@BooksActivity, "Файл успешно загружен", Toast.LENGTH_SHORT).show()
                    bookViewModel.loadAllBooks() // Перезагрузка списка книг
                } else {
                    val errorBody = response.errorBody()?.string()
                    Log.e("BooksActivity", "Ошибка сервера: ${response.code()}, $errorBody")
                    Toast.makeText(this@BooksActivity, "Ошибка сервера: ${response.code()}", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<BookResponse>, t: Throwable) {
                Log.e("BooksActivity", "Ошибка при загрузке: ${t.message}", t)
                Toast.makeText(this@BooksActivity, "Ошибка при загрузке файла", Toast.LENGTH_SHORT).show()
            }
        })
    }

    /**
     * Преобразует URI в файл.
     */
    private fun uriToFile(uri: Uri): File {
        val fileName = getFileName(uri)
        val tempFile = File.createTempFile("upload_", fileName, cacheDir)
        contentResolver.openInputStream(uri)?.use { inputStream ->
            tempFile.outputStream().use { outputStream ->
                inputStream.copyTo(outputStream)
            }
        }
        return tempFile
    }

    /**
     * Получает имя файла из URI.
     */
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

    private fun updateButtonStyles(isAllSelected: Boolean) {
        if (isAllSelected) {
            allBooksButton.setImageResource(R.drawable.adjustable_button)
            favoriteBooksButton.setImageResource(R.drawable.old_button)
        } else {
            allBooksButton.setImageResource(R.drawable.adjustable_button_v2)
            favoriteBooksButton.setImageResource(R.drawable.old_button_v2)
        }
    }
}
