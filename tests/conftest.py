"""测试共享配置"""

import pytest

EN_SRT = """1
00:00:00,000 --> 00:00:04,200
Hello

2
00:00:04,820 --> 00:00:10,000
World
"""

ZH_SRT = """1
00:00:00,000 --> 00:00:04,200
你好

2
00:00:04,820 --> 00:00:10,000
世界
"""


@pytest.fixture
def en_srt_file(tmp_path):
    f = tmp_path / "en.srt"
    f.write_text(EN_SRT, encoding="utf-8")
    return f


@pytest.fixture
def zh_srt_file(tmp_path):
    f = tmp_path / "zh.srt"
    f.write_text(ZH_SRT, encoding="utf-8")
    return f
