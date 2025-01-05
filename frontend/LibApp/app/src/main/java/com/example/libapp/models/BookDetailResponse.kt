package com.example.libapp.models

data class BookDetailResponse(
    val title: String?,
    val authors: String?,
    val annotation: String?,
    val progress: Int,
    val totalPages: Int,
    val textBlocks: List<String>,
    val status: String,
    val compressionLevel: Int,
    val compressedText: Map<String, List<String>>? = null
)
