import LLaMA

def edit_text(text):
    result = LLaMA.llama(text, "edit", 0)
    return result
