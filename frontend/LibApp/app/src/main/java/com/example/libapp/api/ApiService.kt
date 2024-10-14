package com.example.libapp.api

import com.example.libapp.models.Book
import com.example.libapp.models.BookResponse
import com.example.libapp.models.UserResponse
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Call
import retrofit2.http.*

interface ApiService {

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
    ): Call<UserResponse>

    @Multipart
    @POST("upload_book")
    fun uploadBook(
        @Part("id") userId: RequestBody,
        @Part file: MultipartBody.Part
    ): Call<BookResponse>

    @GET("get_user_books")
    fun getUserBooks(
        @Query("userId") userId: String
    ): Call<List<Book>>
}
