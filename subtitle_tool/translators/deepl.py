"""DeepL 翻译器（演示策略模式）"""

import requests

from .base import Translator


class DeepLTranslator(Translator):
    """用 DeepL API 翻译"""

    def __init__(
        self,
        api_key: str,
        url: str = "https://api-free.deepl.com/v2/translate",
    ) -> None:
        self.api_key = api_key
        self.url = url

    def translate(self, text: str) -> str:
        """调用 DeepL 翻译单段文本"""
        resp = requests.post(
            self.url,
            headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
            data={
                "text": text,
                "target_lang": "ZH",
            },
        )
        resp.raise_for_status()
        return resp.json()["translations"][0]["text"]
