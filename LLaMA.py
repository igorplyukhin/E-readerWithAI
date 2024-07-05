import requests
def prompts(context, mode, count_symbols):
    prompt_questions = {
        "messages": [
            {"role": "user", "content": f"Запрос: Необходимо проверить читателя на понимание текста. "
                                        f"Составь вопрос полностью на русском языке по фрагменту текста, который проверит понимание читателя фрагмента текста."
                                        f"Напиши этот вопрос и 4 варианта ответа на этот вопрос, где только 1 верный, укажи  только номер ответа который является верным.###"
                                        f"Формат вывода:"
                                        f"###"
                                        f'"Вопрос?"'
                                        f"1.Ответ 1 "
                                        f"2.Ответ 2 "
                                        f"3.Ответ 3 "
                                        f"4.Ответ 4 "
                                        f'"номер верного ответа"'
                                        f"###"
                                        f"Напиши только эту информацию, ничего лишнего"
                                        f"Исходный текст: \n {context}"}
        ]
    }
    prompt_sum = {
        "messages": [
            {"role": "user", "content": f"Запрос: Необходимо сократить исходный текст, сохранив его смысл. "
                                        f"Пиши только на русском языке"
                                        f"Этот текст является частью большого текста, учитывай это"
                                        f"Сократи этот текст, сохраняя максимальное количество подробностей"
                                        f"Напиши только сокращенный текст, ничего больше"
                                        f"Не пиши фраз по типу 'Сокащенный текст'"
                                        f"Исходный текст: \n {context}"}
        ]
      }
    prompt_sum_at_time = {
        "messages": [
            {"role": "user", "content": f"Запрос: Необходимо сократить текст в определенное количество символов, который является частью большого текста, сохранив смысл"
                                        f"Пиши только на русском языке"
                                        f"Этот текст является частью большого текста, учитывай это"
                                        f"Сократи этот текст сохранив смысл СТРОГО до {count_symbols} символов(+-20)"
                                        f"Напиши только текст, без добавлений от себя"
                                        f"Исходный текст: \n {context}"}
        ]
     }
    if mode == 'sum':
        prompt = prompt_sum
    if mode == 'questions':
        prompt = prompt_questions
    if mode == 'sum at time':
        prompt = prompt_sum_at_time
    return prompt



def llama(context, mode, count_symbols):
    url = "http://5.39.220.103:5009/ask"
    prompt = prompts(context, mode, count_symbols)
    response = requests.post(url, json=prompt)

    if response.status_code == 200:
        response_data = response.json()
        return response_data['response']
    else:
        return f"Error: {response.status_code}, {response.text}"
