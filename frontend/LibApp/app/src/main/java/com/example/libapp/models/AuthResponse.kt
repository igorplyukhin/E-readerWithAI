package com.example.libapp.models

data class AuthResponse(
    val status: String,
    val message: String,
    val userId: String?
)

