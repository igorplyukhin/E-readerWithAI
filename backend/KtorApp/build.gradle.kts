val kotlin_version: String by project
val logback_version: String by project

plugins {
    kotlin("jvm") version "2.0.20"
    id("io.ktor.plugin") version "3.0.0-rc-2"
    id("org.jetbrains.kotlin.plugin.serialization") version "2.0.20"
}

kotlin {
    jvmToolchain(21) // Указываем поддержку Java 21
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

group = "com.example"
version = "0.0.1"

application {
    mainClass.set("com.example.ApplicationKt")

    val isDevelopment: Boolean = project.ext.has("development")
    applicationDefaultJvmArgs = listOf("-Dio.ktor.development=$isDevelopment")
}

repositories {
    mavenCentral()
}

dependencies {
    // Обновлённые зависимости Ktor
    implementation("io.ktor:ktor-server-core:3.0.0-rc-2")
    implementation("io.ktor:ktor-server-netty:3.0.0-rc-2")
    implementation("io.ktor:ktor-server-content-negotiation:3.0.0-rc-2")
    implementation("io.ktor:ktor-serialization-kotlinx-json:3.0.0-rc-2")
    implementation("io.ktor:ktor-server-call-logging:3.0.0-rc-2")
    implementation("io.ktor:ktor-server-default-headers:3.0.0-rc-2")

    // MongoDB
    implementation("org.mongodb:mongodb-driver-sync:4.9.1")

    // Корутины
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.1")

    // Логирование
    implementation("ch.qos.logback:logback-classic:1.4.11")
    implementation("org.slf4j:slf4j-api:2.0.16")

    // Apache Tika для обработки файлов
    implementation("org.apache.tika:tika-core:1.28.4")
    implementation("org.apache.tika:tika-parsers:1.28.4")

    // BCrypt для хеширования паролей
    implementation("org.mindrot:jbcrypt:0.4")

    // Дополнительные зависимости
    // ...

    testImplementation("io.ktor:ktor-server-tests:2.3.4")
    testImplementation(kotlin("test"))
}
