package com.example.libapp.api

import com.example.libapp.models.AuthResponse
import com.example.libapp.models.BookDetailResponse
import com.example.libapp.models.BookResponse
import com.example.libapp.models.CompressionResponse
import com.example.libapp.models.TestResponse
import com.example.libapp.models.UserBooksResponse
import okhttp3.MultipartBody
import retrofit2.Call
import retrofit2.http.*

interface ApiService {

    // Метод регистрации пользователя
    @FormUrlEncoded
    @POST("api/user/register")
    fun registerUser(
        @Field("login") login: String,
        @Field("password") password: String
    ): Call<AuthResponse>

    // Метод авторизации пользователя
    @FormUrlEncoded
    @POST("api/user/login")
    fun loginUser(
        @Field("login") login: String,
        @Field("password") password: String
    ): Call<AuthResponse>

    // Метод получения данных пользователя
    @GET("api/user/get")
    fun getUser(
        @Query("login") login: String
    ): Call<UserBooksResponse>

    // Метод загрузки книги
    @Multipart
    @POST("api/book/upload")
    fun uploadBook(
        @Query("user_id") userId: String,
        @Part file: MultipartBody.Part
    ): Call<BookResponse>

    // Метод для получения детальной информации о книге
    @GET("api/book/detail")
    fun getBookDetail(
        @Query("bookId") bookId: String
    ): Call<BookDetailResponse>

    // Метод для обновления уровня сжатия книги
    @PUT("api/book/updateCompressionLevel")
    fun updateBookCompressionLevel(
        @Query("bookId") bookId: String,
        @Body compressionLevel: Map<String, Int>
    ): Call<Void>

    // Метод для вызова сжатия текста книги
    @POST("api/gigachat/compress-book")
    fun compressBook(
        @Query("book_id") bookId: String,
        @Query("compression_level") compressionLevel: Int
    ): Call<CompressionResponse>

    @PATCH("/api/book/updateProgress")
    fun updateBookProgress(
        @Query("bookId") bookId: String,
        @Query("blockStopBook") blockStopBook: Int,
        @Query("totalPages") totalPages: Int
    ): Call<Map<String, Int>>

    //Mетод для получения теста по вопросам
    @POST("/api/gigachat/generate-test")
    fun generateTest(
        @Query("book_id") bookId: String
    ): Call<TestResponse>
}
