package com.example.libapp.api

import com.example.libapp.models.AuthResponse
import com.example.libapp.models.BookDetailResponse
import com.example.libapp.models.BookPageResponse
import com.example.libapp.models.BookResponse
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

    // Метод для получения содержимого конкретной страницы
    @GET("api/book/page")
    fun getBookPage(
        @Query("bookId") bookId: String,
        @Query("page") pageNumber: Int
    ): Call<BookPageResponse>
}
