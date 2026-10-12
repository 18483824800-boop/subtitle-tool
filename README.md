# 字幕工具 (Subtitle Tool)

用 Ollama 本地模型翻译 SRT 字幕，并合并双语字幕。

## 功能

- 用本地 Ollama 模型翻译英文字幕为中文
- 合并英文和中文字幕为双语字幕
- 支持命令行操作

## 安装

安装 Python 依赖：

    pip3 install -r requirements.txt

确保 Ollama 已运行：

    ollama serve
    ollama pull qwen2.5:7b

## 使用

翻译字幕：

    python3 main.py translate audio.srt

合并双语字幕：

    python3 main.py merge audio.srt audio.zh.srt audio.bilingual.srt

## 配置

修改 `config.yaml` 可调整模型、超时等参数。

## 测试

    python3 -m pytest tests/

## 开发

### 项目结构

    subtitle_tool/
    ├── subtitle_tool/          源码包
    │   ├── __init__.py         包入口
    │   ├── parse.py            SRT 解析
    │   ├── translate.py        翻译
    │   ├── merge.py            合并
    │   └── config.py           配置
    ├── tests/                  测试
    │   ├── conftest.py         共享 fixture
    │   ├── test_parse.py
    │   ├── test_merge.py
    │   └── test_translate.py
    ├── config.yaml
    ├── requirements.txt
    ├── README.md
    └── main.py

### 运行测试
    python3 -m pytest tests/ -v

### 加新测试

在 `tests/` 下创建 `test_xxx.py`，函数名以 `test_` 开头：

    def test_something():
        assert 1 + 1 == 2

## 依赖

- Python 3.8+
- Ollama
- requests
- pyyaml
- pytest