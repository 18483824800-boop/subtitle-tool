"""翻译模块"""

from .base import Translator
from .ollama import OllamaTranslator
from .deepl import DeepLTranslator

__all__ = ["Translator", "OllamaTranslator", "DeepLTranslator"]
