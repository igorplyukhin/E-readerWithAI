package com.example.utils

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.MongoCollection
import com.mongodb.client.MongoDatabase
import org.bson.Document
import org.slf4j.Logger
import org.slf4j.LoggerFactory

object DatabaseFactory {
    private val logger: Logger = LoggerFactory.getLogger(DatabaseFactory::class.java)

    private lateinit var mongoClient: MongoClient
    private lateinit var database: MongoDatabase

    /**
     * Инициализирует подключение к MongoDB.
     * Читает параметры подключения из переменных окружения.
     */
    fun init() {
        try {
            val connectionString = System.getenv("MONGODB_URI") ?: "mongodb://mongo:27018/bookdb"
            val dbName = "bookdb" // Или можно извлечь из строки подключения

            logger.info("Инициализация подключения к MongoDB с строкой подключения: $connectionString")
            val settings = MongoClientSettings.builder()
                .applyConnectionString(ConnectionString(connectionString))
                .build()

            mongoClient = MongoClients.create(settings)
            database = mongoClient.getDatabase(dbName)
            logger.info("Подключение к MongoDB успешно установлено. Используемая база данных: $dbName")
        } catch (e: Exception) {
            logger.error("Ошибка при подключении к MongoDB: ${e.message}", e)
            throw e // Перебрасываем исключение, чтобы приложение не запускалось без подключения к БД
        }
    }

    /**
     * Получает коллекцию пользователей.
     * @return Коллекция `users`.
     */
    fun getUsersCollection(): MongoCollection<Document> {
        ensureInitialized()
        return database.getCollection("users")
    }

    /**
     * Получает коллекцию книг.
     * @return Коллекция `books`.
     */
    fun getBooksCollection(): MongoCollection<Document> {
        ensureInitialized()
        return database.getCollection("books")
    }

    /**
     * Получает коллекцию текстовых блоков.
     * @return Коллекция `text_blocks`.
     */
    fun getTextBlocksCollection(): MongoCollection<Document> {
        ensureInitialized()
        return database.getCollection("text_blocks")
    }

    /**
     * Закрывает подключение к MongoDB.
     */
    fun close() {
        if (::mongoClient.isInitialized) {
            logger.info("Закрытие подключения к MongoDB...")
            mongoClient.close()
            logger.info("Подключение к MongoDB закрыто.")
        }
    }

    /**
     * Проверяет, инициализирована ли база данных.
     * @throws IllegalStateException Если база данных не инициализирована.
     */
    private fun ensureInitialized() {
        if (!::mongoClient.isInitialized || !::database.isInitialized) {
            throw IllegalStateException("DatabaseFactory не инициализирован. Вызовите DatabaseFactory.init() перед использованием.")
        }
    }
}
