"""生成默认分享卡片 public/og-default.png（1200x630）。

用法：python scripts/make-og.py
改完 SITE 里的标题后重新跑一次即可。
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "og-default.png"

W, H = 1200, 630
BG = (250, 249, 247)
INK = (28, 26, 23)
SOFT = (85, 80, 74)
FAINT = (139, 133, 125)
ACCENT = (184, 66, 15)

TITLE = "灰度"
TAGLINE = "工程实践 · 系统设计 · 踩坑复盘"
FOOTER = "huang7269.github.io"

FONT_CANDIDATES_BOLD = [
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
]
FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/segoeui.ttf",
]


def load_font(size: int, candidates: list[str]) -> ImageFont.FreeTypeFont:
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default(size)


img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# 顶部/底部细线
draw.rectangle([0, 0, W, 6], fill=ACCENT)

# 左侧装饰：竖线 + 方块
draw.rectangle([90, 168, 96, 400], fill=ACCENT)

title_font = load_font(96, FONT_CANDIDATES_BOLD)
tag_font = load_font(32, FONT_CANDIDATES)
foot_font = load_font(26, FONT_CANDIDATES)

draw.text((140, 160), TITLE, font=title_font, fill=INK)
draw.text((140, 300), TAGLINE, font=tag_font, fill=SOFT)

# 底部：域名 + 一条横线
draw.line([(140, 470), (W - 90, 470)], fill=(230, 225, 218), width=2)
draw.text((140, 500), FOOTER, font=foot_font, fill=FAINT)

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
