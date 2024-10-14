package com.example.libapp

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Запуск AuthActivity вместо отображения MainActivity
        val intent = Intent(this, AuthActivity::class.java)
        startActivity(intent)

        // Завершаем MainActivity, чтобы оно не оставалось в стеке
        finish()
    }
}
