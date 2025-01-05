from typing import List
import logging

logger = logging.getLogger(__name__)

def split_into_blocks(text: str, block_size: int = 1000) -> List[str]:
    """
    Разделяет текст на блоки заданного размера, завершая каждый блок на границе предложений.
    """
    import re
    blocks = []
    start_index = 0
    sentence_endings = re.compile(r'[.!?…](?=\s|$)')

    while start_index < len(text):
        # Определяем конец текущего блока
        end_index = min(start_index + block_size, len(text))
        if end_index < len(text):
            match = list(sentence_endings.finditer(text, start_index, end_index))
            if match:
                end_index = match[-1].end()
        # Добавляем блок
        blocks.append(text[start_index:end_index].strip())
        start_index = end_index

    # Логируем размеры блоков
    logger.info(f"Количество блоков: {len(blocks)}")
    logger.info(f"Длины блоков: {[len(block) for block in blocks]}")

    return blocks

