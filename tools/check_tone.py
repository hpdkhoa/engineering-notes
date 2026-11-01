"""Scans the .md and .html prose in this repository for my writing rules and common AI tone.

Rules:
no dash as punctuation, sentences of 28 words or fewer, no assurance words, no trust-me phrases, no passive voice
(English) and no "được" passive (Vietnamese), no owner framing, no AI-tone words.
Code spans, code blocks, URLs, tables' code and HTML tags are skipped.
"""

import re
import sys
from pathlib import Path

DASHES = ["—", "–", " -- ", " - "]
BANNED = ["clearly", "obviously", "simply", "of course", "it is easy to see", "needless to say", "trust me",
          "available on request", "under nda", "i can go deeper", "happy to discuss", "defend"]
OWNER = ["owner's words", "the owner", "owner:", "in my own words", "lời chủ dự án", "chủ dự án"]
AI_TONE = ["delve", "leverage", "leveraging", "seamless", "seamlessly", "robust", "comprehensive", "crucial", "pivotal",
           "cutting-edge", "cutting edge", "state-of-the-art", "empower", "unlock", "unleash", "streamline", "holistic",
           "innovative", "game-changer", "game changer", "meticulous", "meticulously", "tapestry", "realm", "foster",
           "elevate", "journey", "landscape", "navigate the", "it's worth noting", "it is worth noting",
           "worth noting", "in summary", "in conclusion", "not only", "let's", "dive into", "deep dive", "boast",
           "showcase", "showcases", "testament", "paramount", "furthermore", "moreover", "additionally", "notably",
           "essentially", "ultimately", "truly", "incredibly", "powerful", "effortless", "effortlessly", "vibrant",
           "ever-evolving", "in today's", "plays a key role", "plays a crucial role", "key role", "a wide range",
           "wide array", "myriad", "plethora", "synergy", "best-in-class", "world-class", "next-level", "rest assured"]
PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being|gets|got)\s+(\w+ly\s+)?(\w+ed|built|made|done|run|shown|"
                     r"seen|kept|left|set|held|found|given|taken|written|read|known|drawn|cut|put|sent|told|bought|"
                     r"brought|caught|chosen|driven|grown|hidden|thrown|worn|broken|spoken|frozen|stolen)\b", re.I)
SKIP_PASSIVE = re.compile(r"\b(is|are|was|were|be|been)\s+(based|used to|supposed|fixed|closed|open|need|tied|"
                          r"limited|bounded|located|called|named|interested|sized|shaped|red|bed|bred|shed|led|fed|"
                          r"wed|sped|bled|need|seed|feed|speed|indeed|hundred|united|related|unrelated)\b", re.I)
# "được" or "bị" before a verb is passive ("công ty được mua lại"); after a verb it means "can" ("chạy được"): allowed
VI_PASSIVE = re.compile(r"\b(được|bị)\s+(mua|chèn|đo|tính|ghi|dùng|tạo|viết|xây|kiểm|chấm|lưu|giữ|đặt|gọi|đưa|làm|"
                        r"chọn|sinh|thêm|xóa|sửa|đổi|công bố|phát hành|cập nhật|chia|nạp|tải|gửi|chạy|duyệt|đánh giá|"
                        r"thiết kế|huấn luyện|triển khai|cài|lấy|trả|so|ước|tìm|đọc|nén|lượng tử|cố định|đóng băng)\b", re.I)


def prose(text: str, html: bool) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " CODE ", text)
    if html:
        text = re.sub(r"<(script|style|pre|code|head)\b.*?</\1>", " ", text, flags=re.S | re.I)
        text = re.sub(r"</?(p|div|h[1-6]|li|td|th|tr|section|header|footer|nav|br|a)\b[^>]*>", "\n\n", text, flags=re.I)
        text = re.sub(r"<span class=\"tag\">.*?</span>", "\n\n", text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = text.replace("&amp;", "&")
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"https?://\S+", " URL ", text)
    return text


def sentences(text: str):
    text = re.sub(r"\s*\|\s*", "\n\n", text)  # every table cell stands alone
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)  # quote markers are not words
    for block in re.split(r"\n\s*\n|\n\s*[-*#]", text):
        block = " ".join(block.split())
        for s in re.split(r"(?<=[.!?])\s+(?=\S)", block):
            if s.strip():
                yield s.strip()


def scan(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    html = path.suffix == ".html"
    text = prose(raw, html)
    low = " " + text.lower() + " "
    out = []
    vi = path.stem.endswith(".vi") or ' lang="vi"' in raw[:400]
    for d in DASHES:
        n = text.count(d)
        if d == " - ":
            n = len(re.findall(r"\w - \w", text))
        if n:
            out.append(f"dash {d.strip() or d!r} x{n}")
    for group, words in (("banned", BANNED), ("owner", OWNER), ("ai-tone", AI_TONE)):
        for w in words:
            n = len(re.findall(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low))
            if n:
                out.append(f"{group} {w!r} x{n}")
    for s in sentences(text):
        words = len(re.findall(r"[\wÀ-ỹ][\wÀ-ỹ'.,%/-]*", s))
        if words > 28:
            out.append(f"long ({words} words): {s[:90]}")
        if not vi:
            for m in PASSIVE.finditer(s):
                if not SKIP_PASSIVE.match(m.group(0)):
                    out.append(f"passive {m.group(0)!r}: {s[:80]}")
    if vi:
        n = len(VI_PASSIVE.findall(text))
        if n:
            out.append(f"vi-passive 'được/bị + verb' x{n}")
    return out


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    files = [p for p in sorted(root.rglob("*")) if p.suffix in (".md", ".html") and ".git" not in p.parts]
    total = 0
    for p in files:
        hits = scan(p)
        total += len(hits)
        print(f"\n{p.relative_to(root)}: {len(hits)}")
        for h in hits[: int(sys.argv[2]) if len(sys.argv) > 2 else 400]:
            print("  " + h)
    print(f"\nTOTAL {total} hits in {len(files)} files")
    sys.exit(1 if total else 0)
