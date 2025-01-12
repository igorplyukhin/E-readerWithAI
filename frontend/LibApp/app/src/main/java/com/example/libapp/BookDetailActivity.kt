package com.example.libapp

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Intent
import android.content.pm.PackageManager
import android.os.*
import android.util.Log
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.example.libapp.api.ApiClient
import com.example.libapp.models.BookDetailResponse
import com.example.libapp.models.CompressionResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.util.concurrent.atomic.AtomicBoolean

class BookDetailActivity : AppCompatActivity() {

    // UI
    private lateinit var progressBar: ProgressBar
    private lateinit var tvProgress: TextView
    private lateinit var btnReadBook: Button
    private lateinit var btnCompressText: Button
    private lateinit var btnBack: ImageButton

    // Идентификаторы
    private var bookId: String? = null

    /**
     * compressionLevel — текущий (по мнению сервера) «активный» уровень.
     * localCompressionLevel — последний выбранный пользователем (слайдер).
     */
    private var compressionLevel: Int = 0
    private var localCompressionLevel: Int = 0
    private var compressedContent: String? = null

    /**
     * Здесь храним карту "уровень" -> список блоков (String), приходящую с сервера (compressedText).
     * Ключи в JSON обычно строковые ("25", "50", "75").
     * Если в Kotlin делаем Map<String, List<String>>, то будем обращаться как
     *   serverCompressions["25"]?.isNotEmpty()
     */
    private var serverCompressions: Map<String, List<String>>? = null

    // Защита от слишком частых запросов
    private var lastRequestTime: Long = 0
    private val REQUEST_INTERVAL = 1000

    // BottomSheet
    private var bottomSheet: BottomSheetCompress? = null

    // Флаг для предотвращения параллельных запросов
    private val isRequestInProgress = AtomicBoolean(false)

    // SharedPreferences (если нужно)
    private val PREFS_NAME = "UserPrefs"
    private val KEY_LAST_COMPRESSION_LEVEL = "last_compression_level"

    // Уведомления
    private val CHANNEL_ID = "compression_channel"
    private val NOTIF_ID_ONGOING = 1001  // «идёт сжатие»
    private val NOTIF_ID_DONE = 1002     // «сжатие завершено»

    // Пуллинг (каждые 2 сек)
    private val handler = Handler(Looper.getMainLooper())
    private var pollingAttempts = 0
    private val MAX_POLLING_ATTEMPTS = 600

    // Регистрация нового API для запуска активности
    private val bookReadingLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            // Обновляем данные книги после завершения BookReadingActivity
            bookId?.let {
                loadBookDetails(it)
            }
        }
    }

    // ------------------------------------------------------

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("BOOK_DETAIL", "onCreate called")
        setContentView(R.layout.activity_book_detail)

        // Разрешение на уведомления (Android 13+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED
            ) {
                Log.d("BOOK_DETAIL", "Requesting POST_NOTIFICATIONS permission")
                requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 999)
            }
        }

        createNotificationChannelIfNeeded()

        // Локальный уровень (если надо)
        val sp = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        localCompressionLevel = sp.getInt(KEY_LAST_COMPRESSION_LEVEL, 0)
        Log.d("BOOK_DETAIL", "Local compressionLevel from prefs = $localCompressionLevel")

        // Инициализируем View
        progressBar = findViewById(R.id.progressBar)
        tvProgress = findViewById(R.id.tvProgress)
        btnReadBook = findViewById(R.id.btnReadBook)
        btnCompressText = findViewById(R.id.btnCompressText)
        btnBack = findViewById(R.id.btnBack)

        btnBack.setOnClickListener {
            Log.d("BOOK_DETAIL", "btnBack clicked -> finish()")
            finish()
        }

        // Получаем ID книги
        bookId = intent.getStringExtra("BOOK_ID")
        Log.d("BOOK_DETAIL", "bookId = $bookId")

        if (bookId == null) {
            Toast.makeText(this, "Ошибка: книга не найдена", Toast.LENGTH_SHORT).show()
            finish()
        } else {
            Log.d("BOOK_DETAIL", "Loading book details for id = $bookId")
            loadBookDetails(bookId!!)
        }

        // Кнопка "Читать книгу"
        btnReadBook.setOnClickListener {
            if (bookId != null) {
                val intent = Intent(this, BookReadingActivity::class.java).apply {
                    putExtra("BOOK_ID", bookId)
                    putExtra("COMPRESSION_LEVEL", compressionLevel)
                    putExtra("COMPRESSED_CONTENT", compressedContent)
                }
                bookReadingLauncher.launch(intent)
            } else {
                Toast.makeText(this, "Ошибка: ID книги отсутствует", Toast.LENGTH_SHORT).show()
            }
        }

        // Кнопка «Сжать»
        btnCompressText.setOnClickListener {
            Log.d("BOOK_DETAIL", "btnCompressText clicked")
            if (bottomSheet == null) {
                bottomSheet = BottomSheetCompress().apply {
                    setOnApplyClickListener { selectedLevel ->
                        Log.d("BOOK_DETAIL", "BottomSheet onApplyClickListener -> selectedLevel = $selectedLevel")
                        localCompressionLevel = selectedLevel
                        saveCompressionLevel(selectedLevel)
                        bottomSheet?.updateSliderValue(localCompressionLevel)

                        performCompressionWithLimit(selectedLevel)
                    }
                }
            }
            bottomSheet?.setCurrentCompressionLevel(localCompressionLevel)
            bottomSheet?.show(supportFragmentManager, "BottomSheetCompress")
        }
    }

    override fun onResume() {
        super.onResume()
        // Обновляем данные книги при возвращении к активности
        bookId?.let {
            loadBookDetails(it)
        }
    }
    // ------------------------------------------------------

    private fun createNotificationChannelIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Log.d("BOOK_DETAIL", "Creating notification channel if needed")
            val name = "Сжатие книги"
            val desc = "Уведомления о процессе сжатия"
            val importance = NotificationManager.IMPORTANCE_DEFAULT
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                description = desc
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun showOngoingCompressionNotification() {
        Log.d("BOOK_DETAIL", "showOngoingCompressionNotification called")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED
            ) {
                Log.d("BOOK_DETAIL", "No POST_NOTIFICATIONS permission -> return")
                return
            }
        }
        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle("Сжимаем книгу...")
            .setContentText("Дождитесь уведомления о завершении")
            .setProgress(0, 0, true)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
        NotificationManagerCompat.from(this).notify(NOTIF_ID_ONGOING, builder.build())
    }

    private fun hideOngoingCompressionNotification() {
        Log.d("BOOK_DETAIL", "hideOngoingCompressionNotification called")
        NotificationManagerCompat.from(this).cancel(NOTIF_ID_ONGOING)
    }

    private fun sendCompressionDoneNotification(compressionLevel: Int) {
        Log.d("BOOK_DETAIL", "sendCompressionDoneNotification called, compressionLevel=$compressionLevel")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                Log.d("BOOK_DETAIL", "No POST_NOTIFICATIONS permission -> return")
                return
            }
        }
        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle("Сжатие завершено!")
            .setContentText("Книга сжата до уровня $compressionLevel%.")
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
        NotificationManagerCompat.from(this).notify(NOTIF_ID_DONE, builder.build())
    }


    private fun saveCompressionLevel(level: Int) {
        Log.d("BOOK_DETAIL", "saveCompressionLevel: $level")
        val sp = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        sp.edit().putInt(KEY_LAST_COMPRESSION_LEVEL, level).apply()
    }

    // ------------------------------------------------------

    private fun loadBookDetails(bookId: String) {
        Log.d("BOOK_DETAIL", "loadBookDetails called, bookId=$bookId")
        setEnabledState(false)

        ApiClient.instance.getBookDetail(bookId).enqueue(object : Callback<BookDetailResponse> {
            override fun onResponse(call: Call<BookDetailResponse>, response: Response<BookDetailResponse>) {
                Log.d("BOOK_DETAIL", "loadBookDetails onResponse: code=${response.code()}")
                setEnabledState(true)
                if (response.isSuccessful && response.body() != null) {
                    val bd = response.body()!!
                    updateUI(bd) // Обновляем UI новыми данными
                } else {
                    Log.d("BOOK_DETAIL", "loadBookDetails -> response NOT successful or body==null")
                    Toast.makeText(this@BookDetailActivity, "Ошибка загрузки книги", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<BookDetailResponse>, t: Throwable) {
                Log.d("BOOK_DETAIL", "loadBookDetails onFailure: ${t.message}")
                setEnabledState(true)
                Toast.makeText(this@BookDetailActivity, "Ошибка сети: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun updateUI(bd: BookDetailResponse) {
        Log.d("BOOK_DETAIL", "updateUI called, bd.compressionLevel=${bd.compressionLevel}")

        // Обновляем заголовок, автора и аннотацию книги
        findViewById<TextView>(R.id.tvBookTitle)?.text = bd.title ?: "Без названия"
        findViewById<TextView>(R.id.tvBookAuthor)?.text = bd.authors ?: "Автор неизвестен"
        findViewById<TextView>(R.id.tvAnnotation)?.text = bd.annotation ?: "Нет описания"

        // Обновляем прогресс чтения
        progressBar.progress = bd.progress
        tvProgress.text = "${bd.progress}%"
        findViewById<TextView>(R.id.tvReadingStatus)?.text = bd.status ?: "Статус неизвестен"

        // Обновляем уровень сжатия
        compressionLevel = bd.compressionLevel
        localCompressionLevel = compressionLevel

        // Сохраняем карту сжатий
        serverCompressions = bd.compressedText
        Log.d("BOOK_DETAIL", "serverCompressions = $serverCompressions")

        // Считываем текстовые блоки для текущего уровня сжатия
        val blockIds = serverCompressions?.get(localCompressionLevel.toString())
        if (!blockIds.isNullOrEmpty()) {
            compressedContent = blockIds.joinToString("\n") { it } // Просто считываем блоки
            Log.d("BOOK_DETAIL", "Compressed content loaded for level=$localCompressionLevel")
        } else {
            compressedContent = null
            Log.d("BOOK_DETAIL", "No compressed content available for level=$localCompressionLevel")
        }

        // Обновляем значение слайдера в BottomSheet
        bottomSheet?.updateSliderValue(localCompressionLevel)

        Log.d("BOOK_DETAIL", "UI updated -> compressionLevel=$compressionLevel localCompressionLevel=$localCompressionLevel")
    }



    private fun performCompressionWithLimit(selLevel: Int) {
        Log.d("BOOK_DETAIL", "performCompressionWithLimit -> selLevel=$selLevel")
        val now = System.currentTimeMillis()
        if (now - lastRequestTime < REQUEST_INTERVAL) {
            Log.d("BOOK_DETAIL", "Too frequent requests, skip")
            Toast.makeText(this, "Слишком частые запросы, подождите...", Toast.LENGTH_SHORT).show()
            return
        }
        lastRequestTime = now

        // Обработка сброса уровня сжатия (0)
        if (selLevel == 0) {
            Log.d("BOOK_DETAIL", "Selected level is 0 -> resetting to original text")
            compressionLevel = 0
            localCompressionLevel = 0
            compressedContent = null
            saveCompressionLevel(0)
            bottomSheet?.updateSliderValue(localCompressionLevel)

            Toast.makeText(this, "Оригинальный текст восстановлен", Toast.LENGTH_SHORT).show()
            updateCompressionLevel(0) // Обновляем поле compressionLevel в базе
            return
        }

        // Проверяем, есть ли уже такой уровень в serverCompressions
        val blocks = serverCompressions?.get(selLevel.toString())
        if (blocks != null && blocks.isNotEmpty()) {
            Log.d("BOOK_DETAIL", "Уровень $selLevel% уже есть (compressedText), skip compressBook")
            Toast.makeText(
                this,
                "Книга уже сжата на $selLevel%",
                Toast.LENGTH_SHORT
            ).show()

            // Обновляем только compressionLevel в базе
            updateCompressionLevel(selLevel)
            return
        }

        // Если уровень уже активный, также обновляем его в базе
        if (selLevel == compressionLevel) {
            Log.d("BOOK_DETAIL", "Already compressed on level=$selLevel in DB => no need compress")
            Toast.makeText(this, "Книга уже сжата на $selLevel%", Toast.LENGTH_SHORT).show()

            // Обновляем только compressionLevel в базе
            updateCompressionLevel(selLevel)
            return
        }

        // Выполняем сжатие и перед началом сохраняем уровень в базе
        updateCompressionLevel(selLevel) // Сохраняем уровень сжатия в базе
        performCompression(selLevel)
    }



    private fun performCompression(level: Int) {
        Log.d("BOOK_DETAIL", "performCompression -> level=$level")
        if (bookId == null) {
            Log.d("BOOK_DETAIL", "performCompression -> bookId is null => error")
            Toast.makeText(this, "Ошибка: нет ID книги", Toast.LENGTH_SHORT).show()
            return
        }
        if (isRequestInProgress.get()) {
            Log.d("BOOK_DETAIL", "performCompression -> isRequestInProgress => skip")
            Toast.makeText(this, "Сжатие уже выполняется...", Toast.LENGTH_SHORT).show()
            return
        }

        isRequestInProgress.set(true)
        setEnabledState(false)

        Log.d("BOOK_DETAIL", "performCompression -> Start compressBook($level)")
        Toast.makeText(
            this,
            "Сжатие на $level% запущено, дождитесь уведомления...",
            Toast.LENGTH_SHORT
        ).show()

        showOngoingCompressionNotification()

        ApiClient.instance.compressBook(bookId!!, level)
            .enqueue(object : Callback<CompressionResponse> {
                override fun onResponse(
                    call: Call<CompressionResponse>,
                    response: Response<CompressionResponse>
                ) {
                    Log.d("BOOK_DETAIL", "compressBook onResponse: code=${response.code()}")
                    if (response.isSuccessful) {
                        Log.d("BOOK_DETAIL", "compressBook -> success")
                    } else {
                        Log.d("BOOK_DETAIL", "compressBook -> response not successful")
                        Toast.makeText(
                            this@BookDetailActivity,
                            "Ошибка сжатия (compressBook)",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                    // Независимо от результата, запускаем пуллинг
                    pollingAttempts = 0
                    startCheckIfCompressionReadyInDB(level)
                }

                override fun onFailure(call: Call<CompressionResponse>, t: Throwable) {
                    Log.d("BOOK_DETAIL", "compressBook onFailure: ${t.message}")
                    Toast.makeText(
                        this@BookDetailActivity,
                        "Ошибка сети compressBook: ${t.message}",
                        Toast.LENGTH_SHORT
                    ).show()
                    // Даже при тайм-ауте или ошибке — запускаем пуллинг
                    pollingAttempts = 0
                    startCheckIfCompressionReadyInDB(level)
                }
            })
    }

    private fun startCheckIfCompressionReadyInDB(neededLevel: Int) {
        Log.d("BOOK_DETAIL", "startCheckIfCompressionReadyInDB -> neededLevel=$neededLevel, pollingAttempts=$pollingAttempts")

        if (pollingAttempts >= MAX_POLLING_ATTEMPTS) {
            Log.d("BOOK_DETAIL", "Polling attempts exceeded. Stopping.")
            isRequestInProgress.set(false)
            hideOngoingCompressionNotification()
            Toast.makeText(
                this@BookDetailActivity,
                "Слишком долго ждём сжатие. Попробуйте позже.",
                Toast.LENGTH_SHORT
            ).show()
            setEnabledState(true)
            return
        }

        ApiClient.instance.getBookDetail(bookId!!).enqueue(object : Callback<BookDetailResponse> {
            override fun onResponse(call: Call<BookDetailResponse>, response: Response<BookDetailResponse>) {
                Log.d("BOOK_DETAIL", "polling getBookDetail onResponse: code=${response.code()}")
                if (response.isSuccessful && response.body() != null) {
                    val bd = response.body()!!
                    Log.d("BOOK_DETAIL", "Current compressionLevel in DB = ${bd.compressionLevel}")

                    val compressedText = bd.compressedText
                    if (compressedText != null && compressedText.containsKey(neededLevel.toString())) {
                        val blocks = compressedText[neededLevel.toString()]
                        if (!blocks.isNullOrEmpty()) {
                            Log.d("BOOK_DETAIL", "Compression ready -> updating UI and notifying user")

                            // Обновляем UI с новыми данными
                            updateUI(bd)

                            // Отправляем уведомление пользователю
                            sendCompressionDoneNotification(neededLevel)

                            hideOngoingCompressionNotification()
                            isRequestInProgress.set(false)
                            setEnabledState(true)
                            return
                        }
                    }
                    Log.d("BOOK_DETAIL", "Compression not ready yet -> continuing polling")
                    pollingAttempts++
                    handler.postDelayed(
                        { startCheckIfCompressionReadyInDB(neededLevel) },
                        5000 // задержка в 2 секунды
                    )
                } else {
                    Log.d("BOOK_DETAIL", "polling -> response not successful or body==null")
                    pollingAttempts++
                    handler.postDelayed(
                        { startCheckIfCompressionReadyInDB(neededLevel) },
                        5000 // задержка в 2 секунды
                    )
                }
            }

            override fun onFailure(call: Call<BookDetailResponse>, t: Throwable) {
                Log.d("BOOK_DETAIL", "polling getBookDetail onFailure: ${t.message}")
                pollingAttempts++
                handler.postDelayed(
                    { startCheckIfCompressionReadyInDB(neededLevel) },
                    5000 // задержка в 2 секунды
                )
            }
        })
    }


    private fun updateCompressionLevel(newLevel: Int) {
        Log.d("BOOK_DETAIL", "updateCompressionLevel($newLevel) called")
        if (bookId == null) {
            Log.d("BOOK_DETAIL", "updateCompressionLevel -> bookId==null => stop")
            isRequestInProgress.set(false)
            setEnabledState(true)
            return
        }
        val valid = listOf(0, 25, 50, 75)
        if (newLevel !in valid) {
            Log.d("BOOK_DETAIL", "updateCompressionLevel -> invalid level=$newLevel => stop")
            isRequestInProgress.set(false)
            setEnabledState(true)
            return
        }

        val data = mapOf("compressionLevel" to newLevel)
        Log.d("BOOK_DETAIL", "Sending data to API: $data with bookId=$bookId")

        ApiClient.instance.updateBookCompressionLevel(bookId!!, data)
            .enqueue(object : Callback<Void> {
                override fun onResponse(call: Call<Void>, response: Response<Void>) {
                    Log.d("BOOK_DETAIL", "updateCompressionLevel onResponse: code=${response.code()}")
                    if (!response.isSuccessful) {
                        Log.d("BOOK_DETAIL", "updateCompressionLevel -> not successful, errorBody=${response.errorBody()?.string()}")
                        Toast.makeText(
                            this@BookDetailActivity,
                            "Ошибка сохранения уровня $newLevel",
                            Toast.LENGTH_SHORT
                        ).show()
                    } else {
                        Log.d("BOOK_DETAIL", "updateCompressionLevel -> success!")
                        // Перезагружаем книгу
                        if (bookId != null) {
                            loadBookDetails(bookId!!)
                        }
                    }
                }

                override fun onFailure(call: Call<Void>, t: Throwable) {
                    Log.d("BOOK_DETAIL", "updateCompressionLevel onFailure: ${t.message}")
                    Toast.makeText(
                        this@BookDetailActivity,
                        "Ошибка сети updateCompressionLevel: ${t.message}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            })
    }


    private fun setEnabledState(enabled: Boolean) {
        Log.d("BOOK_DETAIL", "setEnabledState($enabled)")
        btnReadBook.isEnabled = enabled
        btnCompressText.isEnabled = enabled
        btnBack.isEnabled = enabled
    }
}