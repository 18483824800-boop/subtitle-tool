"""翻译模块"""

import time
import requests


def translate_text(text, model, ollama_url, timeout=120, max_retries=3, retry_delay=2):
    """调用 Ollama 翻译单段文本"""
    prompt = (
        "You are a professional subtitle translator. "
        "Translate the following text to Chinese. "
        "You must translate every word. Do not leave any words untranslate. "
        "Only output the translation, no explanation, no quotes:\n\n"
        f"{text}"
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # 降低随机性，翻译更稳定
        },
    }

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(
                ollama_url, json=payload, timeout=timeout, proxies={"http": None, "https": None}
            )
            resp.raise_for_status()
            result = resp.json().get("response", "").strip()
            if result:
                return result
        except Exception as e:
            if attempt < max_retries:
                print(f"  [重试 {attempt}/{max_retries}] {e}")
                time.sleep(retry_delay)
            else:
                print(f"  [失败] {e}")
                return text  # 失败就返回原文

    return text
