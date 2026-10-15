"""Google 翻译器（演示适配器模式）"""

import requests

from .base import Translator


class GoogleTranslator(Translator):
    """用 Google Translate API 翻译"""

    def __init__(
        self,
        api_key: str,
        url: str = "https://translation.googleapis.com/language/translate/v2",
    ) -> None:
        self.api_key = api_key
        self.url = url

    def translate(self, text: str) -> str:
        """调用 Google 翻译单段文本"""
        resp = requests.post(
            self.url,
            params={"key": self.api_key},
            json={
                "q": text,
                "target": "zh-CN",
            },
        )
        resp.raise_for_status()
        return resp.json()["data"]["translations"][0]["translatedText"]
