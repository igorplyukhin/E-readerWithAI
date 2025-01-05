package com.example.libapp

import android.app.Dialog
import android.content.DialogInterface
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageButton
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.android.material.slider.Slider

class BottomSheetCompress : BottomSheetDialogFragment() {

    private var onApplyClickListener: ((Int) -> Unit)? = null
    private var onDismissListener: (() -> Unit)? = null // Слушатель на закрытие окна
    private var currentCompressionLevel: Int = 0 // Текущее значение уровня сжатия

    fun setOnApplyClickListener(listener: (Int) -> Unit) {
        onApplyClickListener = listener
    }

    fun setOnDismissListener(listener: () -> Unit) {
        onDismissListener = listener
    }

    fun setCurrentCompressionLevel(level: Int) {
        currentCompressionLevel = level
    }

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        return BottomSheetDialog(requireContext(), R.style.CustomBottomSheetDialogTheme)
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.bottom_sheet_compress, container, false)

        val slider = view.findViewById<Slider>(R.id.sliderReadingTime)
        val btnApply = view.findViewById<Button>(R.id.btnApply)
        val btnClose = view.findViewById<ImageButton>(R.id.btnClose)

        slider.value = currentCompressionLevel.toFloat()

        btnApply.setOnClickListener {
            onApplyClickListener?.invoke(slider.value.toInt())
            dismiss()
        }

        btnClose.setOnClickListener {
            dismiss()
        }

        return view
    }

    override fun onDismiss(dialog: DialogInterface) {
        super.onDismiss(dialog)
        onDismissListener?.invoke() // Вызываем слушатель на закрытие
    }

    fun updateSliderValue(level: Int) {
        val slider = view?.findViewById<Slider>(R.id.sliderReadingTime)
        slider?.value = level.toFloat()
    }
}

