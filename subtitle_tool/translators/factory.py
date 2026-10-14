"""翻译器工厂"""

from .base import Translator
from .deepl import DeepLTranslator
from .ollama import OllamaTranslator


def create_translator(name: str, config: dict) -> Translator:
    """根据名字创建翻译器

    Args:
        name: 翻译器名字（"ollama" 或 "deepl")
        config: 配置字典

    Returns:
        Translator 实例

    Raises:
        ValueError: 未知翻译器名字
    """
    if name == "ollama":
        ollama = config["ollama"]
        return OllamaTranslator(
            model=ollama["model"],
            url=ollama["url"],
            timeout=ollama["timeout"],
            max_retries=ollama["max_retries"],
            retry_delay=ollama["retry_delay"],
        )
    elif name == "deepl":
        deepl = config.get("deepl", {})
        return DeepLTranslator(
            api_key=deepl.get("api_key", ""),
            url=deepl.get("url", "https://api-free.deepl.com/v2/translate"),
        )
    else:
        raise ValueError(f"未知翻译器: {name}")
