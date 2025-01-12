package com.example.libapp.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.libapp.R
import com.example.libapp.models.Book

class BookAdapter(
    private var books: List<Book>,
    private val onItemClick: (Book) -> Unit // Лямбда для обработки кликов
) : RecyclerView.Adapter<BookAdapter.BookViewHolder>() {

    inner class BookViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tvBookTitle)
        val tvAuthor: TextView = view.findViewById(R.id.tvBookAuthor)
        val progressBar: ProgressBar = view.findViewById(R.id.progressReading)
        val tvAnnotation: TextView = view.findViewById(R.id.tvAnnotation)
        val tvReadingProgress: TextView = view.findViewById(R.id.tvReadingProgress)
        val tvReadingStatus: TextView = view.findViewById(R.id.tvReadingStatus)

        fun bind(book: Book) {
            tvTitle.text = book.title ?: "Без названия"
            tvAuthor.text = book.author ?: "Неизвестно"
            tvAnnotation.text = book.annotation ?: "Нет аннотации"
            tvReadingProgress.text = "${book.progress ?: 0}%"
            tvReadingStatus.text = book.status ?: "Неизвестно"
            progressBar.progress = book.progress ?: 0

            itemView.setOnClickListener {
                onItemClick(book)
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BookViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_book, parent, false)
        return BookViewHolder(view)
    }

    override fun onBindViewHolder(holder: BookViewHolder, position: Int) {
        val book = books[position]
        holder.bind(book)
    }

    override fun getItemCount(): Int = books.size

    fun updateBooks(newBooks: List<Book>) {
        books = newBooks
        notifyDataSetChanged()
    }
}

