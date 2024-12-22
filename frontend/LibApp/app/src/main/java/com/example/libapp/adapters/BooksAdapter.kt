package com.example.libapp.adapters

import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.libapp.R
import com.example.libapp.models.Book

class BookAdapter(private var books: List<Book>) : RecyclerView.Adapter<BookAdapter.BookViewHolder>() {

    inner class BookViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tvBookTitle)
        val tvAuthor: TextView = view.findViewById(R.id.tvBookAuthor)
        val progressBar: ProgressBar = view.findViewById(R.id.progressReading)
        val tvDescription: TextView = view.findViewById(R.id.tvDescription)
        val tvReadingProgress: TextView = view.findViewById(R.id.tvReadingProgress)
        val tvReadingStatus: TextView = view.findViewById(R.id.tvReadingStatus)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BookViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_book, parent, false)
        return BookViewHolder(view)
    }

    override fun onBindViewHolder(holder: BookViewHolder, position: Int) {
        val book = books[position]
        Log.d("BookAdapter", "Отрисовка книги: ${book.title}")
        holder.tvTitle.text = book.title
        holder.tvAuthor.text = book.author
        holder.tvDescription.text = book.description
        holder.tvReadingProgress.text = book.progress.toString() + "%"
        holder.tvReadingStatus.text = book.status
        holder.progressBar.progress = book.progress
    }


    override fun getItemCount(): Int = books.size

    fun updateBooks(newBooks: List<Book>) {
        Log.d("BookAdapter", "Обновляем список книг: ${newBooks.size}")
        books = newBooks
        notifyDataSetChanged()
    }

}
