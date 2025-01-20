package com.example.libapp.api

import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {
    private const val BASE_URL = "http://185.104.249.252:9333/"

    // Настроим OkHttpClient с тайм-аутами
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)  // Тайм-аут для подключения
        .readTimeout(60, TimeUnit.SECONDS)     // Тайм-аут для чтения данных
        .writeTimeout(60, TimeUnit.SECONDS)    // Тайм-аут для записи данных
        .build()

    val instance: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)  // Устанавливаем клиент с тайм-аутами
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
