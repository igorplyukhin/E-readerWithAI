package com.example.libapp

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.widget.Button
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.libapp.adapters.BooksAdapter
import com.example.libapp.api.ApiClient
import com.example.libapp.models.Book
import com.example.libapp.models.BookResponse
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File

class BooksActivity : AppCompatActivity() {

    private lateinit var rvBooks: RecyclerView
    private lateinit var btnUploadBook: Button
    private var userId: String? = null
    private val books = mutableListOf<Book>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_books)

        rvBooks = findViewById(R.id.rvBooks)
        btnUploadBook = findViewById(R.id.btnUploadBook)

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

    private fun uploadBook(userId: String, fileUri: Uri) {
        val userIdBody = userId.toRequestBody("text/plain".toMediaTypeOrNull())
        val file = uriToFile(fileUri)
        val requestFile = file.asRequestBody("application/octet-stream".toMediaTypeOrNull())
        val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

        ApiClient.instance.uploadBook(userIdBody, filePart).enqueue(object : Callback<BookResponse> {
            override fun onResponse(call: Call<BookResponse>, response: Response<BookResponse>) {
                if (response.isSuccessful && response.body()?.status == "success") {
                    Toast.makeText(this@BooksActivity, "Book uploaded successfully", Toast.LENGTH_SHORT).show()

                    // Добавление новой книги в список с переданным filePath
                    val newBook = Book(
                        idBook = response.body()?.fileId ?: "",
                        title = file.name,
                        author = "Unknown",
                        description = "Description",
                        nameFile = file.name,
                        filePath = file.absolutePath
                    )

                    books.add(newBook)
                    rvBooks.adapter?.notifyItemInserted(books.size - 1)
                } else {
                    val message = response.body()?.message ?: "Unknown error"
                    Toast.makeText(this@BooksActivity, "Upload failed: $message", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<BookResponse>, t: Throwable) {
                Toast.makeText(this@BooksActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }


    private fun loadBooks() {
        userId?.let { id ->
            ApiClient.instance.getUserBooks(id).enqueue(object : Callback<List<Book>> {
                override fun onResponse(call: Call<List<Book>>, response: Response<List<Book>>) {
                    if (response.isSuccessful) {
                        books.clear()
                        books.addAll(response.body() ?: emptyList())
                        rvBooks.adapter?.notifyDataSetChanged()
                    }
                }

                override fun onFailure(call: Call<List<Book>>, t: Throwable) {
                    Toast.makeText(this@BooksActivity, "Error loading books: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }
    }

    private fun openBookDetail(book: Book) {
        val intent = Intent(this, BookDetailActivity::class.java)
        intent.putExtra("BOOK_PATH", book.nameFile)
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
