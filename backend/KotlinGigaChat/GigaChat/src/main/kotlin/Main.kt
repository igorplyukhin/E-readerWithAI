package org.example

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.apache.pdfbox.Loader
import org.apache.pdfbox.text.PDFTextStripper
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.*
import okhttp3.OkHttpClient
import java.security.cert.CertificateException
import javax.net.ssl.HostnameVerifier
import javax.net.ssl.SSLContext
import javax.net.ssl.SSLSocketFactory
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

const val TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
const val CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
const val AUTHORIZATION_HEADER = "Basic ZTkxZjVmMGMtODQ0NS00ZTUwLWExY2QtYWJmMTJhMGY3MDVmOjUzZDA2OWE1LTUxNTAtNDJlNy05OTc1LTEzNDhkNWZhNWM2MA=="
const val MAX_GIGACHAT_TOKENS = 4096 // Предположительно, максимальная длина ответа в токенах

var authToken: String? = null

fun getUnsafeOkHttpClient(): OkHttpClient {
    return try {
        // Создаём доверяющий менеджер, который не проверяет сертификаты
        val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
            @Throws(CertificateException::class)
            override fun checkClientTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {
            }

            @Throws(CertificateException::class)
            override fun checkServerTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {
            }

            override fun getAcceptedIssuers(): Array<java.security.cert.X509Certificate> {
                return arrayOf()
            }
        })

        // Инициализируем SSL-контекст с доверяющим менеджером
        val sslContext = SSLContext.getInstance("SSL")
        sslContext.init(null, trustAllCerts, java.security.SecureRandom())
        val sslSocketFactory: SSLSocketFactory = sslContext.socketFactory

        // Создаём клиента с увеличенными таймаутами
        OkHttpClient.Builder()
            .sslSocketFactory(sslSocketFactory, trustAllCerts[0] as X509TrustManager)
            .hostnameVerifier(HostnameVerifier { _, _ -> true })
            .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS) // Увеличиваем Connect Timeout
            .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)    // Увеличиваем Read Timeout
            .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)   // Увеличиваем Write Timeout
            .build()
    } catch (e: Exception) {
        throw RuntimeException(e)
    }
}

// Функция для получения токена доступа
fun getToken(scope: String = "GIGACHAT_API_CORP") {
    val rqUid = UUID.randomUUID().toString()
    val client = getUnsafeOkHttpClient()
    val formBody = FormBody.Builder()
        .add("scope", scope)
        .build()
    val request = Request.Builder()
        .url(TOKEN_URL)
        .header("Content-Type", "application/x-www-form-urlencoded")
        .header("Accept", "application/json")
        .header("RqUID", rqUid)
        .header("Authorization", AUTHORIZATION_HEADER)
        .post(formBody)
        .build()
    try {
        client.newCall(request).execute().use { response ->
            if (response.isSuccessful) {
                val jsonResponse = response.body?.string()
                val jsonObject = JSONObject(jsonResponse)
                authToken = jsonObject.getString("access_token")
                println("Токен успешно получен.")
            } else {
                println("Не удалось получить токен доступа: ${response.code} ${response.body?.string()}")
            }
        }
    } catch (e: Exception) {
        println("Ошибка при запросе токена доступа: ${e.message}")
    }
}

// Функция для отправки сообщения в GigaChat
fun sendToGigaChat(systemMessage: String, message: String, temperature: Double = 0.87, topP: Double = 0.47): String? {
    if (authToken == null) {
        println("Ошибка: Токен не получен. Пожалуйста, проверьте авторизацию.")
        return null
    }
    val client = getUnsafeOkHttpClient()
    val jsonPayload = JSONObject().apply {
        put("model", "GigaChat-Pro:latest")
        put(
            "messages", JSONArray().put(JSONObject().put("role", "system").put("content", systemMessage))
                .put(JSONObject().put("role", "user").put("content", message))
        )
        put("temperature", temperature)
        put("top_p", topP)
        put("n", 1)
        put("stream", false)
        put("max_tokens", MAX_GIGACHAT_TOKENS)
        put("repetition_penalty", 1.07)
        put("update_interval", 0)
        put("function_call", "auto")
    }

    val requestBody = jsonPayload.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
    val request = Request.Builder()
        .url(CHAT_URL)
        .header("Authorization", "Bearer $authToken")
        .header("Content-Type", "application/json")
        .post(requestBody)
        .build()
    try {
        client.newCall(request).execute().use { response ->
            if (response.isSuccessful) {
                val jsonResponse = response.body?.string()
                val responseObject = JSONObject(jsonResponse)
                val choices = responseObject.getJSONArray("choices")
                if (choices.length() > 0) {
                    val compressedContent = choices.getJSONObject(0)
                        .getJSONObject("message")
                        .getString("content")
                    return compressedContent
                } else {
                    println("Не удалось получить содержимое ответа.")
                    return null
                }
            } else {
                println("Ошибка при отправке в GigaChat: ${response.code} ${response.body?.string()}")
                return null
            }
        }
    } catch (e: Exception) {
        println("Ошибка при выполнении запроса в GigaChat API: ${e.message}")
        return null
    }
}

// Функция для загрузки и разбиения PDF на чанки
fun loadAndChunkPdf(filePath: String, chunkSize: Int = 1000): List<String> {
    val file = File(filePath)
    if (!file.exists()) {
        println("Файл не найден: $filePath")
        return emptyList()
    }

    return Loader.loadPDF(file).use { document ->
        val stripper = PDFTextStripper()
        val text = stripper.getText(document)
        val cleanedText = text.replace("\n", " ").replace("\r", "").split("\\s+".toRegex()).joinToString(" ")
        val chunks = cleanedText.chunked(chunkSize)
        println("Загружено ${chunks.size} чанков текста из PDF.")
        chunks
    }
}

// Функция для обработки и контроля сжатия блоков
fun compressBlockWithRetry(block: String, compressionRate: Int, maxAttempts: Int = 3): String? {
    val targetMinLength = (block.length - (block.length * ((compressionRate + 20) / 100.0))).toInt()
    val targetMaxLength = (block.length - (block.length * ((compressionRate - 20) / 100.0))).toInt()
    var attempt = 0
    var bestResult: String? = null
    var bestLengthDifference = Int.MAX_VALUE // Изменили на Int

    while (attempt < maxAttempts) {
        println("\nПопытка ${attempt + 1} сжать блок до диапазона $targetMinLength - $targetMaxLength символов...")
        val systemMessage = (
                "Сожми входной текст на указанное количество процентов от исходного размера, сохранив при этом исходный смысл и контекст." +
                        "Если в тексте присутствуют формулы или определения, сохраняй их в исходном виде." +
                        "Избегай излишней детализации, но постарайся сохранить логическую структуру и последовательность изложения." +
                        "Рассмотри возможность использования таких методов, как обобщение текста, извлечение сущности или замена слов, чтобы уменьшить размер текста." +
                        "Удаляй повторяющиеся и ненужные слова из следующего текста. Особое внимание удели канцеляризмам." +
                        "Убедись, что объём сжатого текста от $targetMinLength до $targetMaxLength символов в десятичной системе счисления.  Текст:\n$block"
                )

        val compressedText = sendToGigaChat(systemMessage, "${compressionRate}%")
        if (compressedText != null) {
            val responseLength = compressedText.length
            println("Длина ответа: $responseLength символов (ожидалось $targetMinLength - $targetMaxLength).")
            if (responseLength in targetMinLength..targetMaxLength) {
                println("Ответ соответствует ожидаемому диапазону.")
                return "Фрагмент:       $compressedText"
            }
            val lengthDifference = kotlin.math.abs(responseLength - targetMinLength) // Это Int
            if (lengthDifference < bestLengthDifference) {
                bestResult = "Фрагмент:       $compressedText"
                bestLengthDifference = lengthDifference
            }
            println("Ответ не попал в диапазон. Повтор запроса с той же настройкой.")
        } else {
            println("Ошибка при получении ответа от GigaChat.")
        }
        attempt++
    }
    return bestResult
}
// Основная функция для обработки PDF и повторного сжатия
fun main() {
    // Шаг 1: Получаем токен
    getToken()
    if (authToken == null) {
        return
    }
    // Шаг 2: Загружаем PDF и разбиваем на блоки по 2500 символов
    val filePath = "./1_lecture.pdf" // Замените на путь к вашему PDF файлу
    val blocks = loadAndChunkPdf(filePath, chunkSize = 2500)

    var finalCompressedText = ""

    // Шаг 3: Цикл по блокам и их сжатию
    while (true) {
        println()
        print("Введите 1 для сжатия текста или 2 для генерации тестов: ")
        val mode = readLine()
        if (mode == "2") {
            val systemMessage = (
                    "Запрос: Необходимо проверить читателя на понимание текста." +
                            "Составь 5 вопросов полностью на русском языке по фрагменту текста, которые проверят понимание читателя фрагмента текста." +
                            "Напиши каждый вопрос и 4 варианта ответа на каждый вопрос, где только 1 верный, укажи только номер ответа который является верным.###" +
                            "Формат вывода:" +
                            "###" +
                            "\"Вопрос 1?\"" +
                            "1.Ответ 1 " +
                            "2.Ответ 2 " +
                            "3.Ответ 3 " +
                            "4.Ответ 4 " +
                            "\"Ответ: номер верного ответа\"" +
                            "###" +
                            "\"Вопрос 2?\"" +
                            "1.Ответ 1 " +
                            "2.Ответ 2 " +
                            "3.Ответ 3 " +
                            "4.Ответ 4 " +
                            "\"Ответ: номер верного ответа\"" +
                            "###" +
                            "... (и так далее для 5)" +
                            "Напиши только эту информацию, ничего лишнего. Не повторяйся." +
                            "Исходный текст: \n$blocks"
                    )
            val result = sendToGigaChat(systemMessage, "5", 1.0, 1.0) // Используем 1.0 вместо 1
            println(result)
        } else if (mode == "1") {
            print("Введите процент сжатия (или 'exit' для завершения): ")
            val compressionRateInput = readLine()
            if (compressionRateInput.equals("exit", ignoreCase = true)) {
                println("Завершение программы.")
                break
            }
            val compressionRate = compressionRateInput?.toIntOrNull()
            if (compressionRate == null) {
                println("Пожалуйста, введите корректное числовое значение.")
                continue
            }
            for ((i, block) in blocks.withIndex()) {
                println("\nСжимаем блок ${i + 1} из ${blocks.size}...")
                val compressedText = compressBlockWithRetry(block, compressionRate)
                if (compressedText != null) {
                    finalCompressedText += compressedText + "\n\n"
                }
            }
            println("\nИтоговый сжатый текст для всех блоков:")
            println(finalCompressedText)
        }
    }
}
