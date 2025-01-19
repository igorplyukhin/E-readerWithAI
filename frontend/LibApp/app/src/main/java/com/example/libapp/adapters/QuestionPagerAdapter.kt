package com.example.libapp.adapters

import android.graphics.Color
import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.RadioButton
import androidx.recyclerview.widget.RecyclerView
import com.example.libapp.databinding.ItemQuestionBinding
import com.example.libapp.models.Question

class QuestionPagerAdapter(
    private val questions: List<Question>,
    private val answerSelectedListener: (Int, Int) -> Unit
) : RecyclerView.Adapter<QuestionPagerAdapter.QuestionViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): QuestionViewHolder {
        val binding = ItemQuestionBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return QuestionViewHolder(binding)
    }

    override fun onBindViewHolder(holder: QuestionViewHolder, position: Int) {
        // Проверяем, что индекс находится в пределах списка вопросов
        if (position < questions.size) {
            val question = questions[position]
            holder.bind(question, position)
        }
    }

    override fun getItemCount(): Int = questions.size

    inner class QuestionViewHolder(private val binding: ItemQuestionBinding) : RecyclerView.ViewHolder(binding.root) {

        fun bind(question: Question, position: Int) {
            binding.tvQuestion.text = question.question

            // Заполнение вариантов ответа
            binding.answerOption1.text = question.answers.getOrNull(0)?.text ?: "Ответ не найден"
            binding.answerOption2.text = question.answers.getOrNull(1)?.text ?: "Ответ не найден"
            binding.answerOption3.text = question.answers.getOrNull(2)?.text ?: "Ответ не найден"
            binding.answerOption4.text = question.answers.getOrNull(3)?.text ?: "Ответ не найден"

            // Логика выбора ответа
            setAnswerClickListener(binding.answerOption1, 0, question, position)
            setAnswerClickListener(binding.answerOption2, 1, question, position)
            setAnswerClickListener(binding.answerOption3, 2, question, position)
            setAnswerClickListener(binding.answerOption4, 3, question, position)

            // Подсветка правильных/неправильных ответов
            highlightAnswers(question)
        }

        private fun setAnswerClickListener(view: RadioButton, answerIndex: Int, question: Question, position: Int) {
            view.setOnClickListener {
                question.selectedAnswer = answerIndex
                answerSelectedListener(position, answerIndex)  // Обработчик для подсветки
                notifyDataSetChanged()  // Обновление UI
            }
        }

        private fun highlightAnswers(question: Question) {
            // Очищаем предыдущие подсветки
            binding.answerOption1.setBackgroundColor(Color.TRANSPARENT)
            binding.answerOption2.setBackgroundColor(Color.TRANSPARENT)
            binding.answerOption3.setBackgroundColor(Color.TRANSPARENT)
            binding.answerOption4.setBackgroundColor(Color.TRANSPARENT)

            // Подсвечиваем правильный или неправильный ответ
            question.selectedAnswer?.let { selectedAnswer ->
                if (question.answers.getOrNull(selectedAnswer)?.is_correct == true) {
                    when (selectedAnswer) {
                        0 -> binding.answerOption1.setBackgroundColor(Color.GREEN)
                        1 -> binding.answerOption2.setBackgroundColor(Color.GREEN)
                        2 -> binding.answerOption3.setBackgroundColor(Color.GREEN)
                        3 -> binding.answerOption4.setBackgroundColor(Color.GREEN)
                    }
                } else {
                    when (selectedAnswer) {
                        0 -> binding.answerOption1.setBackgroundColor(Color.RED)
                        1 -> binding.answerOption2.setBackgroundColor(Color.RED)
                        2 -> binding.answerOption3.setBackgroundColor(Color.RED)
                        3 -> binding.answerOption4.setBackgroundColor(Color.RED)
                    }
                    // Подсвечиваем правильный ответ
                    question.answers.indexOfFirst { it.is_correct }.let {
                        when (it) {
                            0 -> binding.answerOption1.setBackgroundColor(Color.GREEN)
                            1 -> binding.answerOption2.setBackgroundColor(Color.GREEN)
                            2 -> binding.answerOption3.setBackgroundColor(Color.GREEN)
                            3 -> binding.answerOption4.setBackgroundColor(Color.GREEN)
                        }
                    }
                }
            }
        }
    }
}
