"""Ollama翻译器"""

import time
import requests

from .base import Translator


class OllamaTranslator(Translator):
    """用Ollama本地模型翻译"""

    def __init__(
        self,
        model: str,
        url: str,
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: int = 2,
    ) -> None:
        self.model = model
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def translate(self, text: str) -> str:
        """调用 Ollama 翻译单段文本"""
        prompt = (
            "You are a professional subtitle translator. "
            "Translate the following text to Chinese. "
            "You must translate every word. Do not leave any words untranslated. "
            "Only output the translation, no explanation, no quotes:\n\n"
            f"{text}"
        )

        from typing import Any
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3},
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.post(
                    self.url,
                    json=payload,
                    timeout=self.timeout,
                    proxies={"http": None, "https": None}, # type: ignore[dict-item]
                )
                resp.raise_for_status()
                result = resp.json().get("response", "").strip()
                if result:
                    return result
            except Exception:
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    return text
        return text
