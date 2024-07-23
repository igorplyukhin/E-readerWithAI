import requests
def prompts(context, mode, count_symbols,question, right_answer):
    prompt_questions = {
        "messages": [
            {"role": "system", "content": f"Запрос: Необходимо проверить читателя на понимание текста. "
                                          f"Составь вопрос полностью на русском языке по фрагменту текста, который проверит понимание читателя фрагмента текста."
                                          f"Напиши этот вопрос и 4 варианта ответа на этот вопрос, где только 1 верный, укажи  только номер ответа который является верным.###"
                                          f"Напиши только эту информацию, ничего лишнего"},
            {f"role": "user", "content": f"Исходный текст: \n {context}"},
            {"role": "assistant", "content": f'"Вопрос?\n"'
                                             f"1.Ответ 1 "
                                             f"2.Ответ 2 "
                                             f"3.Ответ 3 "
                                             f"4.Ответ 4 "
                                             f'"номер верного ответа"'
             }

        ]
    }
    prompt_open_questions = {
        "messages": [
            {"role": "system", "content": f"Запрос: Необходимо проверить читателя на понимание текста. "
                                          f"Составь вопрос подразумевающий развернутый ответ полностью на русском языке по фрагменту текста, который проверит понимание читателя фрагмента текста."
                                          f"Напиши этот вопрос"
                                          f"Напиши только эту информацию, ничего лишнего"},
            {"role": "user", "content": f"Исходный текст: \n {context}"},
            {"role": "assistant", "content": f'"Вопрос?\n"'
             }

        ]
    }


    prompt_right_answer = {
        "messages": [
            {"role": "system", "content": f"Запрос: Найди в этом тексте подтверждение того, что ответ - {question} на этот вопрос - {right_answer} является верным "
                                        f"Если подтверждение нашлось напиши 'Да', иначе 'Нет'"
                                        f"Для ответа используй только этот текст"
                                        f"Напиши только эту информацию, ничего лишнего"
                                        f"Исходный текст: \n {context}"}
        ]
    }
    prompt_questions_add = {
        "messages": [
            {"role": "system", "content": f"Запрос: Необходимо проверить читателя на понимание текста. "
                                        f"Составь другой вопрос полностью на русском языке по фрагменту текста, который проверит понимание читателя фрагмента текста."
                                        f"Напиши этот вопрос отличающийся от предыдущего и 4 варианта ответа на этот вопрос, где только 1 верный, укажи  только номер ответа который является верным.###"
                                        f"Формат вывода:"
                                        f"Напиши только эту информацию, ничего лишнего"},
            {"role": "user", "content":  f"Исходный текст: \n {context}"
             },
            {"role": "assistant", "content": f'"Вопрос?\n"'
                                             f"1.Ответ 1 "
                                             f"2.Ответ 2 "
                                             f"3.Ответ 3 "
                                             f"4.Ответ 4 "
                                             f'"номер верного ответа"'
             }


        ]
    }
    prompt_sum = {
        "messages": [
            {"role": "system", "content": f"Запрос: Необходимо сократить исходный текст, сохранив его смысл. "
                                        f"Пиши только на русском языке"
                                        f"Этот текст является частью большого текста, учитывай это"
                                        f"Сократи этот текст, сохраняя максимальное количество подробностей"
                                        f"Напиши только сокращенный текст, ничего больше"
                                        f"Не пиши фраз по типу 'Сокащенный текст'"},
            {"role": "user", "content": f"Исходный текст: \n {context}"}
        ]
      }

    prompt_sum_at_time = {
        "messages": [
            {"role": "system", "content": f"Запрос: Твоя задача извлечь из указанного фрагмента текста, который является частью большого текста, необходимую информацию и написать в точном количестве предложений."
                                        f"Пиши только на русском языке"
                                        f"Этот текст является частью большого текста, учитывай это"
                                        f"Описывай максимально подробно."
                                        f"Напиши краткое содержимое части книги объемом в {count_symbols} предложений."
                                        f"Если исходный текст состоит из {count_symbols} предложений или меньше, то выведи исходный текст"
                                        f"Ответ должен быть цельным связным текстом, который может заменить исходный текст"
                                        f"Напиши только текст, без добавлений от себя"
                                        f"Не пиши фраз по типу 'Сокращенный текст'"
             },
            {"role": "user",
             "content": f"Исходный текст: \n {context}"
             },
            {"role": "assistant",
             "content": "'Суммаризированный текст'"}

        ]
     }
    prompt_retelling = {
        "messages": [
            {"role": "system",
             "content": f"Запрос: Необходимо сделать пересказ книги"
                        f"Используй только русский язык"
                        },
            {"role": "user",
             "content": f"Книга: \n {context}"
             },
            {"role": "assistant",
             "content": "'текст'"}
        ]
    }
    prompt_edit = {
        "messages": [
            {"role": "system",
             "content": f"Запрос: После обработки текста появились лишние символы"
                        f"Сделай из этого текста связный текст без лишних символов(Определи язык по контексту)"
                        f"Не сокращай исходный текст"
                        f"Только исправь проблемные места"
                        f"Напиши только исправленный текст, не дописывай от себя фраз по типу 'Исправленный текст:'"},
            {"role": "user",
             "content": f"Исходный текст: \n {context}"
             },
            {"role": "assistant",
             "content": "'Исправленный текст'"}
        ]
    }
    prompt_edit_q = {
        "messages": [
            {"role": "system", "content": f"Запрос: Необходимо проверить читателя на понимание текста. "
                                        f"Пиши на русском языке"
                                        f"На входе вопрос и варианты ответа, оставь всё как есть только исправь проблемные места(символы из языков которого нет в контексте)."
                                        f"Напиши только эту информацию, ничего лишнего"},
            {"role": "user", "content": f"Исходный текст: \n {context}"},
            {"role": "assistant", "content": f'"Вопрос?\n"'
                                             f"1.Ответ 1 "
                                             f"2.Ответ 2 "
                                             f"3.Ответ 3 "
                                             f"4.Ответ 4 "
                                             f'"номер верного ответа"'
             }

        ]
    }
    prompt_about_book = {
        "messages": [
            {"role": "system", "content": f"Запрос: Напиши кратко о чем эта книга "
                                        f"Пиши на русском языке"
                                        f"Напиши только эту информацию, ничего лишнего"},
            {"role": "user", "content": f"Исходный текст: \n {context}"},
        ]
    }
    prompt_name_book = {
        "messages": [
            {"role": "system", "content": f"Запрос: По отрывку из книги определи, что это за книга. Напиши только автора и название книги"
                                          f"Если не можешь однозначно определить название книги, то напиши 'Нет'"
                                        f"Пиши на русском языке"
                                        f"Напиши только эту информацию, ничего лишнего"},
            {"role": "user", "content": f"Исходный текст: \n {context}"},
            {"role": "user", "content": f"Title:Название книги\n"
                                        f"Author:Имя автора"}
        ]
    }
    prompt_advice = {
        "messages": [
            {"role": "system", "content": f"Запрос: Посоветуй книги похожие на приведенную ниже"
                                          f"Напиши только список книг и краткое описание"
                                          f"Пиши только на русском языке, это важно"
                                          f"Напиши только эту информацию, ничего лишнего"},
            {"role": "user", "content": f"Книга: \n {context}"},
        ]
    }
    prompt_translate = {
        "messages": [
            {"role": "system", "content": f"Запрос: Если данный текст на другом языке переведи на русский"
                                          f"Если текст на русском выведи этот же текст"
                                          f"Пиши только на русском языке, это важно"
                                          f"Напиши только эту информацию, ничего лишнего"},
            {"role": "user", "content": f"Текст: \n {context}"},
        ]
    }
    if mode == 'sum':
        prompt = prompt_sum
    if mode == 'questions':
        prompt = prompt_questions
    if mode == 'sum at time':
        prompt = prompt_sum_at_time
    if mode == "edit":
        prompt = prompt_edit
    if mode == "questions_add":
        prompt = prompt_questions_add
    if mode == "questions_edit":
        prompt = prompt_edit_q
    if mode == "right answer":
        prompt = prompt_right_answer
    if mode == "about book":
        prompt = prompt_about_book
    if mode == "retelling":
        prompt = prompt_retelling
    if mode == "name":
        prompt = prompt_name_book
    if mode == "advice":
        prompt = prompt_advice
    if mode == "open questions":
        prompt = prompt_open_questions
    if mode == "translate":
        prompt = prompt_translate
    return prompt



def llama(context, mode, count_symbols, question, right_answer):
    url = "http://5.39.220.103:5009/ask"
    prompt = prompts(context, mode, count_symbols,question, right_answer)
    response = requests.post(url, json=prompt)

    if response.status_code == 200:
        response_data = response.json()
        return response_data['response']
    else:
        return f"Error: {response.status_code}, {response.text}"
