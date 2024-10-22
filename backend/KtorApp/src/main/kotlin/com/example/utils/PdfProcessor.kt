package com.example.utils

import org.apache.pdfbox.pdmodel.PDDocument
import org.apache.pdfbox.text.PDFTextStripper
import java.io.File

class PdfProcessor(private val filePath: String) {

    fun extractText(): String {
        val document = PDDocument.load(File(filePath))
        val pdfStripper = PDFTextStripper()
        val text = pdfStripper.getText(document)
        document.close()
        return text
    }
}
