"""字幕合并块"""

from .parse import parse_srt, build_srt


def merge_srt(en_file, zh_file, output_file):
    en_blocks = parse_srt(en_file)
    zh_blocks = parse_srt(zh_file)
    if len(en_blocks) != len(zh_blocks):
        print(f"⚠️片段数不一致: 英文 {len(en_blocks)}, 中文 {len(zh_blocks)}")
        n = min(len(en_blocks), len(zh_blocks))
    else:
        n = len(en_blocks)
    merged_blocks = []
    for i in range(n):
        en = en_blocks[i]
        zh = zh_blocks[i]
        merged_blocks.append(
            {
                "idx": en["idx"],
                "timecode": en["timecode"],
                "text": f"{en['text']}\n{zh['text']}",
            }
        )
    result = build_srt(merged_blocks)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"✅ 合并完成: {output_file}")
