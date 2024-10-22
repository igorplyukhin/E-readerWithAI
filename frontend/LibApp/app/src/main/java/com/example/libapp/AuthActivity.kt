package com.example.libapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.libapp.api.ApiClient
import com.example.libapp.models.UserResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import androidx.activity.enableEdgeToEdge

class AuthActivity : AppCompatActivity() {

    private var userId: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_auth)

        val etLogin = findViewById<EditText>(R.id.etLogin)
        val etPassword = findViewById<EditText>(R.id.etPassword)
        val btnLogin = findViewById<Button>(R.id.btnLogin)
        val btnRegister = findViewById<Button>(R.id.btnRegister)

        btnLogin.setOnClickListener {
            val login = etLogin.text.toString()
            val password = etPassword.text.toString()
            if (login.isNotEmpty() && password.isNotEmpty()) {
                loginUser(login, password)
            } else {
                Toast.makeText(this, "Please enter login and password", Toast.LENGTH_SHORT).show()
            }
        }

        btnRegister.setOnClickListener {
            val login = etLogin.text.toString()
            val password = etPassword.text.toString()
            if (login.isNotEmpty() && password.isNotEmpty()) {
                registerUser(login, password)
            } else {
                Toast.makeText(this, "Please enter login and password", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun loginUser(login: String, password: String) {
        ApiClient.instance.login(login, password).enqueue(object : Callback<UserResponse> {
            override fun onResponse(call: Call<UserResponse>, response: Response<UserResponse>) {
                if (response.isSuccessful && response.body()?.status == "success") {
                    userId = login // Сохраняем ID пользователя
                    val intent = Intent(this@AuthActivity, BooksActivity::class.java)
                    intent.putExtra("USER_ID", userId) // Передаем ID пользователя
                    startActivity(intent)
                    Toast.makeText(this@AuthActivity, "Login successful", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this@AuthActivity, "Login failed: ${response.body()?.message}", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<UserResponse>, t: Throwable) {
                Toast.makeText(this@AuthActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun registerUser(login: String, password: String) {
        ApiClient.instance.register(login, password).enqueue(object : Callback<UserResponse> {
            override fun onResponse(call: Call<UserResponse>, response: Response<UserResponse>) {
                if (response.isSuccessful && response.body()?.status == "success") {
                    userId = response.body()?.userId // Получаем userId из ответа
                    val intent = Intent(this@AuthActivity, BooksActivity::class.java)
                    intent.putExtra("USER_ID", userId) // Передаем userId
                    startActivity(intent)
                    Toast.makeText(this@AuthActivity, "Registration successful", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this@AuthActivity, "Registration failed: ${response.body()?.message}", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<UserResponse>, t: Throwable) {
                Toast.makeText(this@AuthActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
