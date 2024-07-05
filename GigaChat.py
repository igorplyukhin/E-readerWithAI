from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

GIGACHAT_USER = 'MmFkNjdmZTQtYTkwZS00N2E2LTgwOTMtOWFjYmFhMjVkZWM0OmUyODMxNzEyLTYzYjgtNDMyMi1iYWM3LWNkY2UzYmJhMWY4Mg=='
client_secret = 'e2831712-63b8-4322-bac7-cdce3bba1f82'

chat = GigaChat(credentials=GIGACHAT_USER, scope="GIGACHAT_API_PERS", verify_ssl_certs=False, model="GigaChat")
system_prompt_questions = (
    f"Запрос: Необходимо проверить читателя на понимание текста. "
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
    f"Исходный текст: \n"
)
system_prompt_sum = (
    f"Запрос: Необходимо сократить исходный текст, сохранив его смысл. "
    f"Пиши только на русском языке"
    f"Этот текст является частью большого текста, учитывай это"
    f"Сократи этот текст, сохраняя максимальное количество подробностей"
    f"Напиши только эту информацию, ничего лишнего"
    f"Исходный текст: \n")
def prompts(mode):
    if mode == "questions":
        return system_prompt_questions
    if mode == "sum":
        return system_prompt_sum
def gigachat(text, mode):
    prompt = prompts(mode)
    messages = [SystemMessage(content=prompt)]
    messages.append(HumanMessage(content=text))
    res = chat.invoke(messages)
    return res.content

