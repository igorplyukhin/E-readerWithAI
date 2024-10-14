package com.example.libapp

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.io.File

class BookDetailActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_book_detail)

        val tvBookContent = findViewById<TextView>(R.id.tvBookContent)
        val bookPath = intent.getStringExtra("BOOK_PATH")

        if (bookPath != null) {
            val file = File(bookPath)
            tvBookContent.text = file.readText()
        } else {
            tvBookContent.text = "Error: Book content not available."
        }
    }
}
