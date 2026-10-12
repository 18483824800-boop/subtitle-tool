"""SRT解析模块"""

import re
from pathlib import Path


def parse_srt(path):
    """解析 SRT 文件，返回 (头部, 字幕块列表, 尾部)"""
    # SRT 格式：序号 + 时间轴 + 文本 + 空行
    content = Path(path).read_text(encoding="utf-8")
    pattern = re.compile(
        r"(\d+)\s*\n"  # 序号
        r"(\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3})\s*\n"  # 时间轴
        r"((?:.+\n?)+?)"  # 文本（可能多行）
        r"(?=\n\s*\n|\Z)",  # 后面跟空行或文件结束
        re.MULTILINE,
    )

    blocks = []
    for match in pattern.finditer(content):
        idx, timecode, text = match.groups()
        blocks.append(
            {
                "idx": idx.strip(),
                "timecode": timecode.strip(),
                "text": text.strip(),
            }
        )

    return blocks


def build_srt(blocks):
    """把字幕块列表重新拼成 SRT 字符串"""
    parts = []
    for b in blocks:
        parts.append(f"{b['idx']}\n{b['timecode']}\n{b['text']}\n")
    return "\n".join(parts)
