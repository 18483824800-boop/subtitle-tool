"""测试google翻译器"""

from unittest.mock import patch
from subtitle_tool.translators import GoogleTranslator


@patch("subtitle_tool.translators.google.requests.post")
def test_google_translate_success(mock_post):
    """测试正常翻译"""
    mock_post.return_value.json.return_value = {
        "data": {"translations": [{"translatedText": "你好"}]}
    }
    mock_post.return_value.raise_for_status.return_value = None

    translator = GoogleTranslator(
        api_key="test-key",
        url="https://translation.googleapis.com/language/translate/v2",
    )
    result = translator.translate("Hello")
    assert result == "你好"


@patch("subtitle_tool.translators.google.requests.post")
def test_google_translate_failure(mock_post):
    """测试请求失败时抛异常"""
    mock_post.return_value.raise_for_status.side_effect = Exception("HTTP error")
    translator = GoogleTranslator(
        api_key="test-key",
        url="https://translation.googleapis.com/language/translate/v2",
    )
    import pytest

    with pytest.raises(Exception, match="HTTP error"):
        translator.translate("Hello")
