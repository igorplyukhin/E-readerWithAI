package com.example.libapp.api

import com.example.libapp.models.BookDetailResponse
import com.example.libapp.models.BookPageResponse
import com.example.libapp.models.BookResponse
import com.example.libapp.models.UserBooksResponse
import com.example.libapp.models.UserResponse
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Call
import retrofit2.http.*

interface ApiService {

    // Существующие методы
    @FormUrlEncoded
    @POST("register")
    fun register(
        @Field("login") login: String,
        @Field("password") password: String
    ): Call<UserResponse>

    @FormUrlEncoded
    @POST("login")
    fun login(
        @Field("login") login: String,
        @Field("password") password: String
    ): Call<UserResponse>

    @FormUrlEncoded
    @POST("get_user")
    fun getUser(
        @Field("login") login: String
    ): Call<UserBooksResponse>

    @Multipart
    @POST("upload_book")
    fun uploadBook(
        @Part("id") userId: RequestBody,
        @Part file: MultipartBody.Part
    ): Call<BookResponse>

    // Новый метод для получения детальной информации о книге
    @GET("get_book_detail")
    fun getBookDetail(
        @Query("id") bookId: String
    ): Call<BookDetailResponse>

    // Новый метод для получения содержимого конкретной страницы
    @GET("get_book_page")
    fun getBookPage(
        @Query("id") bookId: String,
        @Query("page") pageNumber: Int
    ): Call<BookPageResponse>
}
