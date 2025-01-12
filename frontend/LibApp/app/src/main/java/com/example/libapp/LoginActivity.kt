package com.example.libapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.libapp.api.ApiClient
import com.example.libapp.models.AuthResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class LoginActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val etLogin = findViewById<EditText>(R.id.loginField)
        val etPassword = findViewById<EditText>(R.id.passwordField)
        val btnLogin = findViewById<Button>(R.id.btnLoginEmail)
        val btnBack = findViewById<ImageButton>(R.id.btnBack)

        btnLogin.setOnClickListener {
            val login = etLogin.text.toString().trim()
            val password = etPassword.text.toString().trim()

            if (login.isNotEmpty() && password.isNotEmpty()) {
                loginUser(login, password)
            } else {
                Toast.makeText(this, "Введите логин и пароль", Toast.LENGTH_SHORT).show()
            }
        }

        btnBack.setOnClickListener {
            finish()
        }
    }

    private fun loginUser(login: String, password: String) {
        ApiClient.instance.loginUser(login, password).enqueue(object : Callback<AuthResponse> {
            override fun onResponse(call: Call<AuthResponse>, response: Response<AuthResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val authResponse = response.body()
                    if (authResponse?.status == "success") {
                        val userId = authResponse.userId
                        val intent = Intent(this@LoginActivity, BooksActivity::class.java)
                        intent.putExtra("USER_ID", userId)
                        startActivity(intent)
                        Toast.makeText(this@LoginActivity, "Вход успешен", Toast.LENGTH_SHORT).show()
                    } else {
                        val errorMessage = authResponse?.message ?: "Неизвестная ошибка"
                        Toast.makeText(this@LoginActivity, "Ошибка входа: $errorMessage", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    val errorMessage = response.errorBody()?.string() ?: "Неизвестная ошибка"
                    Toast.makeText(this@LoginActivity, "Ошибка входа: $errorMessage", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<AuthResponse>, t: Throwable) {
                Toast.makeText(this@LoginActivity, "Ошибка: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

}