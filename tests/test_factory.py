"""测试翻译器工厂"""

import pytest

from subtitle_tool.translators import (
    DeepLTranslator,
    OllamaTranslator,
    GoogleTranslator,
    create_translator,
)


def test_create_ollama():
    """测试创建的ollama翻译器"""
    config = {
        "ollama": {
            "model": "qwen2.5:7b",
            "url": "http://localhost:11434/api/generate",
            "timeout": 120,
            "max_retries": 3,
            "retry_delay": 2,
        }
    }
    translator = create_translator("ollama", config)
    assert isinstance(translator, OllamaTranslator)
    assert translator.model == "qwen2.5:7b"


def test_create_deepl():
    """测试创建的deepl翻译器"""
    config = {
        "deepl": {
            "api_key": "test-key",
            "url": "https://api-free.deepl.com/v2/translate",
        }
    }
    translator = create_translator("deepl", config)
    assert isinstance(translator, DeepLTranslator)
    assert translator.api_key == "test-key"


def test_create_google():
    """测试google翻译器"""
    config = {
        "google": {
            "api_key": "test-key",
            "url": "https://translation.googleapis.com/language/translate/v2",
        }
    }
    translator = create_translator("google", config)
    assert isinstance(translator, GoogleTranslator)
    assert translator.api_key == "test-key"


def test_create_unknown():
    """测试未知翻译器"""
    config = {}
    with pytest.raises(ValueError, match="未知翻译器"):
        create_translator("unknown", config)


def test_create_deepl_without_config():
    """测试没配deepl时用默认值"""
    config = {}
    translator = create_translator("deepl", config)
    assert isinstance(translator, DeepLTranslator)
    assert translator.api_key == ""
