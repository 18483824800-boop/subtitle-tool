"""测试SRT解析"""

from subtitle_tool.parse import parse_srt, build_srt


def test_parse_count(en_srt_file):
    """测试解析出正确的片段数"""
    blocks = parse_srt(en_srt_file)
    assert len(blocks) == 2


def test_parse_content(en_srt_file):
    """测试解析内容是否正确"""

    blocks = parse_srt(en_srt_file)
    assert blocks[0]["text"] == "Hello"
    assert blocks[1]["text"] == "World"


def test_build_srt():
    """测试重新拼装"""
    blocks = [
        {"idx": "1", "timecode": "00:00:00,000 --> 00:00:04,200", "text": "Hello"},
        {"idx": "2", "timecode": "00:00:04,820 --> 00:00:10,000", "text": "World"},
    ]
    result = build_srt(blocks)

    assert "Hello" in result
    assert "World" in result
