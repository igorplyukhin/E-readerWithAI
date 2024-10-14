FROM openjdk:21-jdk-slim

WORKDIR /app

# Копирование файлов для сборки
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle ./gradle
COPY gradlew ./
COPY src ./src

# Сборка проекта
RUN chmod +x ./gradlew
RUN ./gradlew installDist

# Открытие порта для Ktor
EXPOSE 8080

# Запуск Ktor-сервера
CMD ["./build/install/KtorApp/bin/KtorApp"]
