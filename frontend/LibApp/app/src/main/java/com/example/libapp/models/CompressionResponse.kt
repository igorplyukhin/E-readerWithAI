package com.example.libapp.models

data class CompressionResponse(
    val bookId: String,
    val compressionLevel: Int,
    val pages: List<String>
)

