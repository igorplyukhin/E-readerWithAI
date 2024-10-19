FROM openjdk:21-jdk-slim

WORKDIR /app

# Установка bash и dos2unix
RUN apt-get update && apt-get install -y bash dos2unix

# Копирование файлов для сборки
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle ./gradle
COPY gradlew ./
COPY src ./src

# Преобразование окончаний строк и установка прав на выполнение gradlew
RUN dos2unix gradlew
RUN chmod +x gradlew

# Сборка проекта с использованием sh
RUN sh gradlew installDist --no-daemon

# Открытие порта для Ktor
EXPOSE 8080

# Запуск Ktor-сервера
CMD ["./build/install/KtorApp/bin/KtorApp"]
