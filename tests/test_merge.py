"""测试字幕合并"""

from subtitle_tool.merge import merge_srt


def test_merge_basic(tmp_path, en_srt_file, zh_srt_file):
    """测试正常合并"""
    output_file = tmp_path / "merged.srt"

    merge_srt(en_srt_file, zh_srt_file, output_file)

    result = output_file.read_text(encoding="utf-8")
    assert "Hello" in result
    assert "你好" in result
    assert "World" in result
    assert "世界" in result


def test_merge_mismatched_count(tmp_path, en_srt_file):
    """测试片段数不一致时，取较小的"""
    zh_file = tmp_path / "zh.srt"
    output_file = tmp_path / "merged.srt"

    zh_short = """1
00:00:00,000 --> 00:00:04,200
你好
"""
    zh_file.write_text(zh_short, encoding="utf-8")

    merge_srt(en_srt_file, zh_file, output_file)

    result = output_file.read_text(encoding="utf-8")
    assert "Hello" in result
    assert "你好" in result
    assert "World" not in result
    assert "世界" not in result


def test_merge_creates_output(tmp_path, en_srt_file, zh_srt_file):
    """测试输出文件被创建"""
    output_file = tmp_path / "merged.srt"

    assert not output_file.exists()  # 调用前不存在

    merge_srt(en_srt_file, zh_srt_file, output_file)

    assert output_file.exists()  # 调用后存在
