package com.example.libapp.models

import android.os.Parcel
import android.os.Parcelable

// Класс Answer должен быть Parcelable
data class Answer(
    val text: String, // Текст ответа
    val is_correct: Boolean // Флаг правильности ответа
) : Parcelable {
    constructor(parcel: Parcel) : this(
        parcel.readString() ?: "",  // Читаем строку для текстового ответа
        parcel.readByte() != 0.toByte()  // Читаем boolean как байт
    )

    override fun writeToParcel(parcel: Parcel, flags: Int) {
        parcel.writeString(text)  // Записываем строку
        parcel.writeByte(if (is_correct) 1 else 0)  // Записываем флаг
    }

    override fun describeContents(): Int = 0

    companion object CREATOR : Parcelable.Creator<Answer> {
        override fun createFromParcel(parcel: Parcel): Answer {
            return Answer(parcel)
        }

        override fun newArray(size: Int): Array<Answer?> {
            return arrayOfNulls(size)
        }
    }
}

// Класс Question должен быть Parcelable
data class Question(
    val question: String, // Вопрос
    val answers: List<Answer>, // Список вариантов ответа
    var selectedAnswer: Int? = null // Индекс выбранного ответа (по умолчанию null, если не выбран)
) : Parcelable {
    constructor(parcel: Parcel) : this(
        parcel.readString() ?: "",  // Читаем строку для текста вопроса
        parcel.createTypedArrayList(Answer.CREATOR) ?: emptyList(),  // Читаем список ответов
        parcel.readValue(Int::class.java.classLoader) as? Int  // Читаем выбранный ответ
    )

    override fun writeToParcel(parcel: Parcel, flags: Int) {
        parcel.writeString(question)  // Записываем текст вопроса
        parcel.writeTypedList(answers)  // Записываем список ответов
        parcel.writeValue(selectedAnswer)  // Записываем выбранный ответ
    }

    override fun describeContents(): Int = 0

    companion object CREATOR : Parcelable.Creator<Question> {
        override fun createFromParcel(parcel: Parcel): Question {
            return Question(parcel)
        }

        override fun newArray(size: Int): Array<Question?> {
            return arrayOfNulls(size)
        }
    }
}

// Класс TestResponse должен быть Parcelable, если он содержит список вопросов
data class TestResponse(
    val questions: List<Question> // Список вопросов
) : Parcelable {
    constructor(parcel: Parcel) : this(
        parcel.createTypedArrayList(Question.CREATOR) ?: emptyList()  // Читаем список вопросов
    )

    override fun writeToParcel(parcel: Parcel, flags: Int) {
        parcel.writeTypedList(questions)  // Записываем список вопросов
    }

    override fun describeContents(): Int = 0

    companion object CREATOR : Parcelable.Creator<TestResponse> {
        override fun createFromParcel(parcel: Parcel): TestResponse {
            return TestResponse(parcel)
        }

        override fun newArray(size: Int): Array<TestResponse?> {
            return arrayOfNulls(size)
        }
    }
}

data class MessageResponse(
    val message: String // Сообщение от сервера
) : Parcelable {
    constructor(parcel: Parcel) : this(
        parcel.readString() ?: ""  // Читаем строку сообщения
    )

    override fun writeToParcel(parcel: Parcel, flags: Int) {
        parcel.writeString(message)  // Записываем сообщение в Parcel
    }

    override fun describeContents(): Int = 0

    companion object CREATOR : Parcelable.Creator<MessageResponse> {
        override fun createFromParcel(parcel: Parcel): MessageResponse {
            return MessageResponse(parcel)
        }

        override fun newArray(size: Int): Array<MessageResponse?> {
            return arrayOfNulls(size)
        }
    }
}
