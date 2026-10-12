# 第 2 周：测试与文档笔记

## 一、本周目标

| 目标         |        说明               |
|-------------|--------------------------|
| 学会写测试    | 用 pytest 写单元测试 |
| 学会用 fixture| 用 conftest.py 消除重复 |
| 学会用 mock   | 模拟外部依赖 |
| 完善文档      | 把测试说明写进 README |


## 二、本周完成

| 天 | 内容 | 状态 |
|----|------|------|
| 第 1 天 | 写 test_parse.py | ✅ |
| 第 2 天 | 写 test_merge.py | ✅ |
| 第 3 天 | 写 test_translate.py（mock） | ✅ |
| 第 4 天 | 写 conftest.py，重构 | ✅ |
| 第 5 天 | 跳过（大同小异） | — |
| 第 6 天 | 完善 README | ✅ |
| 第 7 天 | 写笔记 | ✅ |


## 三、测试基础

### 命名规则

| 类型     | 规则      | 例子           |
|----------|----------|---------------|
| 测试文件 | test_*.py | test_parse.py |
| 测试函数 | test_*    | test_parse_count|
| 测试类   | Test*     | TestRequests |

### 测试结构

准备 → 执行 → 断言

举例：

def test_parse_count(en_srt_file):
    blocks = parse_srt(en_srt_file)      # 执行
    assert len(blocks) == 2               # 断言

### 常用工具

工具	                 用途
assert	                断言
pytest.raises	        断言抛异常
pytest.mark.parametrize	参数化
fixture	                注入测试依赖
tmp_path	            临时目录 fixture

### 运行测试

# 跑单个文件
python3 -m pytest tests/test_parse.py -v

# 跑整个目录
python3 -m pytest tests/ -v

# 只跑名字含关键字的
python3 -m pytest tests/ -k "parse" -v

## 我的测试

### test_parse.py

"""测试 SRT 解析"""
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

parse_srt 解析出正确片段数

parse_srt 解析出正确内容

build_srt 拼装正确

### test_merge.py

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
    assert not output_file.exists()
    merge_srt(en_srt_file, zh_srt_file, output_file)
    assert output_file.exists()

测了什么：

正常合并

片段数不一致时取较小

输出文件被创建

### test_translate.py

"""测试翻译模块"""
from unittest.mock import patch
from subtitle_tool.translate import translate_text


@patch("subtitle_tool.translate.requests.post")
def test_translate_success(mock_post):
    """测试正常翻译"""
    mock_post.return_value.json.return_value = {"response": "你好"}
    mock_post.return_value.raise_for_status.return_value = None
    result = translate_text(
        "Hello",
        model="qwen2.5:7b",
        ollama_url="http://localhost:11434/api/generate",
    )
    assert result == "你好"


@patch("subtitle_tool.translate.requests.post")
def test_translate_failure_returns_original(mock_post):
    """测试翻译失败返回原文"""
    mock_post.side_effect = Exception("Network error")
    result = translate_text(
        "Hello",
        model="qwen2.5:7b",
        ollama_url="http://localhost:11434/api/generate",
        max_retries=1,
        retry_delay=0,
    )
    assert result == "Hello"


@patch("subtitle_tool.translate.requests.post")
def test_translate_empty_response(mock_post):
    """测试模型返回空时返回原文"""
    mock_post.return_value.json.return_value = {"response": ""}
    mock_post.return_value.raise_for_status.return_value = None
    result = translate_text(
        "Hello",
        model="qwen2.5:7b",
        ollama_url="http://localhost:11434/api/generate",
        max_retries=1,
        retry_delay=0,
    )
    assert result == "Hello"

测了什么：

正常翻译（成功）

翻译失败（返回原文）

模型返回空（返回原文）

为什么测三种：

代码有 3 条路，每条都要测（分支覆盖）

## conftest.py

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
    """创建英文测试 SRT 文件"""
    f = tmp_path / "en.srt"
    f.write_text(EN_SRT, encoding="utf-8")
    return f


@pytest.fixture
def zh_srt_file(tmp_path):
    """创建中文测试 SRT 文件"""
    f = tmp_path / "zh.srt"
    f.write_text(ZH_SRT, encoding="utf-8")
    return f
作用：

放共享常量和 fixture

pytest 自动加载

同目录及子目录的测试都能用

不需要 import

## mock 基础

mock 是什么
假装调用外部服务，返回固定结果。

from unittest.mock import patch

@patch("subtitle_tool.translate.requests.post")
def test_something(mock_post):
    mock_post.return_value.json.return_value = {"response": "你好"}
    ...

patch 路径怎么写
写"被测模块里怎么写的"。

translate.py 里：

python
import requests

def translate_text(...):
    resp = requests.post(...)
patch 路径：

python
@patch("subtitle_tool.translate.requests.post")
不是 @patch("requests.post")。

常用属性
属性	          用途
return_value	设置假返回
side_effect	    设置抛异常

## 重构

改之前
python
SAMPLE_SRT = """..."""

def test_parse_count(tmp_path):
    test_file = tmp_path / "test.srt"
    test_file.write_text(SAMPLE_SRT, encoding="utf-8")
    blocks = parse_srt(test_file)
    assert len(blocks) == 2
改之后
python
def test_parse_count(en_srt_file):
    blocks = parse_srt(en_srt_file)
    assert len(blocks) == 2
变化：

删掉了 SAMPLE_SRT（移到 conftest.py）

删掉了 tmp_path 参数（改用 en_srt_file）

删掉了 write_text（fixture 里做了）

测试函数从 5 行变 3 行

## 测试结构

tests/
├── __init__.py
├── conftest.py          ← 共享 fixture 和常量
├── test_parse.py        ← 用 en_srt_file
├── test_merge.py        ← 用 en_srt_file 和 zh_srt_file
└── test_translate.py    ← 用 mock

## 核心概念

概念	                  说明
测试结构	              准备 → 执行 → 断言
测试命名	              test_.py、test_
assert	                 断言
pytest.raises	         测异常
pytest.mark.parametrize	参数化
fixture	                测试的准备函数
tmp_path	            临时目录 fixture
conftest.py	            共享 fixture 和常量
mock	                假装调用外部服务
@patch	                替换函数
分支覆盖	            代码有几条路就测几条
重构后重跑测试	         确认没破坏功能

## 总结

第 2 周 = 给 subtitle_tool 写测试 + 完善文档。
核心：测试结构（准备 → 执行 → 断言），用 fixture 消除重复，用 mock 模拟外部依赖。






