"""翻译器抽象基类"""


class Translator:
    """翻译器抽象基类"""

    def translate(self, text: str) -> str:
        """翻译单段文本"""
        raise NotImplementedError("The 'translate' method must be implemented")
