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

class RegisterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        val etLogin = findViewById<EditText>(R.id.loginField)
        val etPassword = findViewById<EditText>(R.id.passwordField)
        val btnRegister = findViewById<Button>(R.id.btnLoginEmail)
        val btnBack = findViewById<ImageButton>(R.id.btnBack)

        btnRegister.setOnClickListener {
            val login = etLogin.text.toString().trim()
            val password = etPassword.text.toString().trim()

            if (login.isNotEmpty() && password.isNotEmpty()) {
                registerUser(login, password)
            } else {
                Toast.makeText(this, "Введите логин и пароль", Toast.LENGTH_SHORT).show()
            }
        }

        btnBack.setOnClickListener {
            finish()
        }
    }

    private fun registerUser(login: String, password: String) {
        ApiClient.instance.registerUser(login, password).enqueue(object : Callback<AuthResponse> {
            override fun onResponse(call: Call<AuthResponse>, response: Response<AuthResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val authResponse = response.body()
                    if (authResponse?.status == "success") {
                        val userId = authResponse.userId
                        val intent = Intent(this@RegisterActivity, BooksActivity::class.java)
                        intent.putExtra("USER_ID", userId)
                        startActivity(intent)
                        Toast.makeText(this@RegisterActivity, "Регистрация успешна", Toast.LENGTH_SHORT).show()
                    } else {
                        val errorMessage = authResponse?.message ?: "Неизвестная ошибка"
                        Toast.makeText(this@RegisterActivity, "Ошибка регистрации: $errorMessage", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    val errorMessage = response.errorBody()?.string() ?: "Неизвестная ошибка"
                    Toast.makeText(this@RegisterActivity, "Ошибка регистрации: $errorMessage", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<AuthResponse>, t: Throwable) {
                Toast.makeText(this@RegisterActivity, "Ошибка: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
