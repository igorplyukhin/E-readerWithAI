import LLaMA


def edit_text(text):
    result = LLaMA.llama(text, "edit", 0)
    return result


def right_answer(answer_llm,  question):
    for _ in range(3):
        result = LLaMA.llama(answer_llm, "right answer", 0, question, answer_llm)
        if "Да" in result or "да" in result:
            print("Без ошибок")
            return 0
        if "Нет" in result or "нет" in result:
            print("Ошибка")
            return 1
