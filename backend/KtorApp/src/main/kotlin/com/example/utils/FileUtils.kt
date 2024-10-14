package com.example.utils

import java.io.File
import java.nio.charset.StandardCharsets
import org.apache.pdfbox.pdmodel.PDDocument
import org.apache.pdfbox.text.PDFTextStripper
import org.apache.tika.Tika
import org.apache.tika.exception.TikaException
import java.io.IOException
import org.xml.sax.SAXException

object FileUtils {

    private val tika = Tika()

    /**
     * Сохраняет файл по указанному пути.
     * @param path Путь для сохранения файла.
     * @param bytes Содержимое файла в виде массива байт.
     */
    fun saveFile(path: String, bytes: ByteArray) {
        val file = File(path)
        file.parentFile.mkdirs()
        file.writeBytes(bytes)
    }

    /**
     * Проверяет расширение файла и конвертирует его в поддерживаемый формат при необходимости.
     * @param filePath Путь к файлу.
     * @return Путь к конвертированному или исходному файлу.
     */
    fun checkAndConvertFile(filePath: String): String {
        val supportedExtensions = listOf("txt", "epub", "pdf")
        val fileExtension = getFileExtension(filePath).lowercase()

        return if (fileExtension in supportedExtensions) {
            when (fileExtension) {
                "txt" -> filePath
                "pdf" -> convertPdfToTxt(filePath)
                "epub" -> convertEpubToTxt(filePath)
                else -> throw UnsupportedOperationException("Неподдерживаемый формат файла")
            }
        } else {
            throw UnsupportedOperationException("Формат файла $fileExtension не поддерживается")
        }
    }

    /**
     * Извлекает расширение файла.
     * @param filePath Путь к файлу.
     * @return Расширение файла.
     */
    private fun getFileExtension(filePath: String): String {
        return filePath.substringAfterLast('.', "")
    }

    /**
     * Конвертирует PDF-файл в текстовый файл (.txt).
     * @param filePath Путь к PDF-файлу.
     * @return Путь к созданному текстовому файлу.
     */
    private fun convertPdfToTxt(filePath: String): String {
        val pdfFile = File(filePath)
        val txtFilePath = filePath.replaceAfterLast('.', "txt")
        val txtFile = File(txtFilePath)

        try {
            PDDocument.load(pdfFile).use { document ->
                val stripper = PDFTextStripper()
                val text = stripper.getText(document)
                txtFile.writeText(text, StandardCharsets.UTF_8)
            }
        } catch (e: IOException) {
            e.printStackTrace()
            throw IOException("Ошибка при конвертации PDF в TXT: ${e.message}")
        }

        return txtFilePath
    }

    /**
     * Конвертирует EPUB-файл в текстовый файл (.txt) с использованием Apache Tika.
     * @param filePath Путь к EPUB-файлу.
     * @return Путь к созданному текстовому файлу.
     */
    private fun convertEpubToTxt(filePath: String): String {
        val epubFile = File(filePath)
        val txtFilePath = filePath.replaceAfterLast('.', "txt")
        val txtFile = File(txtFilePath)

        try {
            val text = tika.parseToString(epubFile)
            txtFile.writeText(text, StandardCharsets.UTF_8)
        } catch (e: IOException) {
            e.printStackTrace()
            throw IOException("Ошибка при конвертации EPUB в TXT: ${e.message}")
        } catch (e: TikaException) {
            e.printStackTrace()
            throw IOException("Ошибка при обработке EPUB файла: ${e.message}")
        } catch (e: SAXException) {
            e.printStackTrace()
            throw IOException("Ошибка при обработке EPUB файла: ${e.message}")
        }

        return txtFilePath
    }
}
