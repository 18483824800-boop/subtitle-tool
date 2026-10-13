"""测试翻译模块"""

from unittest.mock import patch
from subtitle_tool.translators import OllamaTranslator


@patch("subtitle_tool.translators.ollama.requests.post")
def test_translate_success(mock_post):
    """测试正常翻译"""
    mock_post.return_value.json.return_value = {"response": "你好"}
    mock_post.return_value.raise_for_status.return_value = None

    translator = OllamaTranslator(
        model="qwen2.5:7b",
        url="http://localhost:11434/api/generate",
    )
    result = translator.translate("Hello")
    assert result == "你好"


@patch("subtitle_tool.translators.ollama.requests.post")
def test_translate_failure_returns_original(mock_post):
    """测试翻译失败返回原文"""
    mock_post.side_effect = Exception("Network error")
    translator = OllamaTranslator(
        model="qwen2.5:7b",
        url="http://localhost:11434/api/generate",
        max_retries=1,
        retry_delay=0,
    )
    result = translator.translate("Hello")
    assert result == "Hello"


@patch("subtitle_tool.translators.ollama.requests.post")
def test_translate_empty_response(mock_post):
    """测试模型返回空时返回原文"""
    mock_post.return_value.json.return_value = {"response": ""}
    mock_post.return_value.raise_for_status.return_value = None

    translator = OllamaTranslator(
        model="qwen2.5:7b",
        url="http://localhost:11434/api/generate",
        max_retries=1,
        retry_delay=0,
    )
    result = translator.translate("Hello")
    assert result == "Hello"
