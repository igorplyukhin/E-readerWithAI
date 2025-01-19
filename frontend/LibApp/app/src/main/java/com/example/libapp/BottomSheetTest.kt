package com.example.libapp

import android.app.Dialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.viewpager2.widget.ViewPager2
import com.example.libapp.adapters.QuestionPagerAdapter
import com.example.libapp.api.ApiClient
import com.example.libapp.databinding.DialogTestSwipeBinding
import com.example.libapp.models.MessageResponse
import com.example.libapp.models.Question
import com.example.libapp.models.TestResponse
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class BottomSheetTest : BottomSheetDialogFragment() {

    private lateinit var questionAdapter: QuestionPagerAdapter
    private var questions: List<Question> = emptyList()
    private var onStartLoadingListener: (() -> Unit)? = null

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val binding = DialogTestSwipeBinding.inflate(inflater, container, false)

        // Обработчик для кнопки "Назад"
        binding.btnCloseTest.setOnClickListener {
            dismiss()  // Закрыть фрагмент (BottomSheet)
        }

        // Показать прогресс-бар сразу
        onStartLoadingListener?.invoke()

        // Получаем переданный ID книги
        val bookId = arguments?.getString("BOOK_ID") ?: return null

        // Запускаем загрузку теста
        loadTestQuestions(bookId, binding)

        return binding.root
    }

    fun setOnStartLoadingListener(listener: () -> Unit) {
        onStartLoadingListener = listener
    }

    // Метод для загрузки вопросов с сервера
    private fun loadTestQuestions(bookId: String, binding: DialogTestSwipeBinding) {
        // Покажем индикатор загрузки и текст
        binding.progressBar.visibility = View.VISIBLE
        binding.tvMessage.visibility = View.VISIBLE  // Показываем текст

        // API вызов для получения вопросов
        ApiClient.instance.generateTest(bookId).enqueue(object : Callback<TestResponse> {
            override fun onResponse(call: Call<TestResponse>, response: Response<TestResponse>) {
                binding.progressBar.visibility = View.GONE // Скрыть прогресс-бар
                binding.tvMessage.visibility = View.GONE // Скрыть текст

                if (response.isSuccessful) {
                    val testResponse = response.body()

                    // Проверяем, если в ответе нет вопросов или они равны null
                    if (testResponse == null || testResponse.questions.isNullOrEmpty()) {
                        // Это может быть сообщение о том, что книгу не начали читать
                        val messageResponse = MessageResponse("Вы ещё не начали читать книгу")
                        binding.tvMessage.text = messageResponse.message
                        binding.tvMessage.visibility = View.VISIBLE
                        return  // Не открываем диалоговое окно, просто показываем сообщение
                    }

                    // Если это тест, заполняем вопросы
                    questions = testResponse.questions
                    setupViewPager(binding)  // Настроить ViewPager с новыми вопросами

                } else {
                    Toast.makeText(requireContext(), "Ошибка сервера", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<TestResponse>, t: Throwable) {
                binding.progressBar.visibility = View.GONE // Скрыть прогресс-бар в случае ошибки
                binding.tvMessage.visibility = View.GONE // Скрыть текст
                Toast.makeText(requireContext(), "Ошибка подключения: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    // Метод для настройки ViewPager2 с адаптером
    private fun setupViewPager(binding: DialogTestSwipeBinding) {
        if (questions.isNotEmpty()) {
            // Устанавливаем адаптер для ViewPager2
            questionAdapter = QuestionPagerAdapter(questions) { position, answerIndex ->
                questions[position].selectedAnswer = answerIndex
                questionAdapter.notifyDataSetChanged()  // Обновление UI после выбора ответа
            }

            binding.viewPagerQuestions.adapter = questionAdapter

            // Слушатель для отображения номера текущего вопроса
            binding.viewPagerQuestions.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
                override fun onPageSelected(position: Int) {
                    super.onPageSelected(position)
                    binding.tvQuestionCounter.text = "${position + 1}/${questions.size}"
                }
            })
        } else {
            Toast.makeText(requireContext(), "Нет доступных вопросов", Toast.LENGTH_SHORT).show()
        }
    }

    // Переопределяем метод onCreateDialog для использования кастомного стиля
    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        return BottomSheetDialog(requireContext(), R.style.CustomBottomSheetDialogTheme)
    }

    companion object {
        fun newInstance(bookId: String, testResponse: TestResponse? = null): BottomSheetTest {
            val fragment = BottomSheetTest()
            val bundle = Bundle()
            bundle.putString("BOOK_ID", bookId)
            bundle.putParcelable("TEST_RESPONSE", testResponse)
            fragment.arguments = bundle
            return fragment
        }
    }
}
