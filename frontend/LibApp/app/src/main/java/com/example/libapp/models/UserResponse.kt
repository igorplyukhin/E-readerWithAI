package com.example.libapp.models

data class UserResponse(
    val status: String,
    val message: String,
    val userId: String? = null
)
