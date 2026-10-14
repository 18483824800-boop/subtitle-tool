#!/usr/bin/env python3
"""字幕工具命令行入口"""

import sys
from pathlib import Path

from subtitle_tool.config import load_config
from subtitle_tool.parse import parse_srt, build_srt
from subtitle_tool.translators import create_translator
from subtitle_tool.merge import merge_srt


def translate_srt(input_file, output_file, config):
    """翻译整个SRT文件"""
    blocks = parse_srt(input_file)
    total = len(blocks)
    print(f"📊 共 {total} 个片段\n")

    translator = create_translator("ollama", config)
    for i, block in enumerate(blocks, 1):
        print(f"[{i}/{total}]")
        block["text"] = translator.translate(block["text"])

    result = build_srt(blocks)
    Path(output_file).write_text(result, encoding="utf-8")
    print(f"\n✅ 翻译完成: {output_file}")


def main():
    if len(sys.argv) < 3:
        print("用法:")
        print("  python3 main.py translate <输入.srt> [输出.srt]")
        print("  python3 main.py merge <英文.srt> <中文.srt> <输出.srt> ")
        sys.exit(1)
    command = sys.argv[1]
    config = load_config()

    if command == "translate":
        input_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else input_file.replace(".srt", ".zh.srt")
        translate_srt(input_file, output_file, config)
    elif command == "merge":
        merge_srt(sys.argv[2], sys.argv[3], sys.argv[4])

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
