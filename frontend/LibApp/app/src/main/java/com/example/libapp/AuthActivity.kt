package com.example.libapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity

class AuthActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_auth)

        val btnLoginEmail = findViewById<Button>(R.id.btnLoginEmail)
        val btnRegister = findViewById<Button>(R.id.btnRegister)

        btnLoginEmail.setOnClickListener {
            // Переход на экран авторизации
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
        }

        btnRegister.setOnClickListener {
            // Переход на экран регистрации
            val intent = Intent(this, RegisterActivity::class.java)
            startActivity(intent)
        }
    }
}
