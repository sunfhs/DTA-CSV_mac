#!/usr/bin/env python3
from pathlib import Path
from subprocess import run

from PIL import Image, ImageDraw, ImageFilter, ImageFont


root = Path(__file__).parent
iconset = root / "build/DTAtoCSV.iconset"
iconset.mkdir(parents=True, exist_ok=True)

font_big = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 116)
font_mid = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 76)
font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 56)

base = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
draw = ImageDraw.Draw(base)

shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
shadow_draw = ImageDraw.Draw(shadow)
shadow_draw.rounded_rectangle((104, 118, 920, 920), radius=190, fill=(0, 0, 0, 62))
base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)))

for y in range(96, 912):
    t = (y - 96) / 816
    color = (
        int(255 * (1 - t) + 229 * t),
        int(248 * (1 - t) + 249 * t),
        int(238 * (1 - t) + 255 * t),
        255,
    )
    draw.line((96, y, 928, y), fill=color, width=1)

mask = Image.new("L", base.size, 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.rounded_rectangle((96, 96, 928, 912), radius=190, fill=255)
base.putalpha(mask)
draw = ImageDraw.Draw(base)
draw.rounded_rectangle((96, 96, 928, 912), radius=190, outline=(36, 44, 55, 255), width=14)

def document_box(x: int, y: int, w: int, h: int, fill: tuple[int, int, int, int], label: str) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=52, fill=(0, 0, 0, 28))
    draw.rounded_rectangle((x, y - 12, x + w, y + h - 12), radius=52, fill=fill, outline=(36, 44, 55, 255), width=10)
    fold = 88
    draw.polygon(
        [(x + w - fold, y - 12), (x + w, y - 12), (x + w, y + fold - 12)],
        fill=(255, 255, 255, 150),
        outline=(36, 44, 55, 255),
    )
    draw.text((x + w / 2, y + 106), label, anchor="mm", fill=(36, 44, 55, 255), font=font_mid)


document_box(176, 248, 272, 360, (255, 217, 184, 255), "DTA")
document_box(576, 248, 272, 360, (181, 232, 217, 255), "CSV")

for i in range(4):
    y = 458 + i * 42
    draw.line((612, y, 812, y), fill=(36, 44, 55, 110), width=8)
for x in [660, 724]:
    draw.line((x, 430, x, 590), fill=(36, 44, 55, 80), width=6)

draw.line((450, 440, 558, 440), fill=(65, 118, 219, 255), width=34)
draw.polygon([(548, 382), (646, 440), (548, 498)], fill=(65, 118, 219, 255))
draw.text((512, 706), "DTA -> CSV", anchor="mm", fill=(36, 44, 55, 255), font=font_small)

for points in [
    [(270, 192), (286, 226), (320, 242), (286, 258), (270, 292), (254, 258), (220, 242), (254, 226)],
    [(760, 690), (772, 716), (798, 728), (772, 740), (760, 766), (748, 740), (722, 728), (748, 716)],
]:
    draw.polygon(points, fill=(255, 210, 80, 255), outline=(36, 44, 55, 255))

base.save(root / "build/DTAtoCSV-preview.png")

sizes = [16, 32, 128, 256, 512]
for size in sizes:
    for scale in [1, 2]:
        px = size * scale
        name = f"icon_{size}x{size}{'@2x' if scale == 2 else ''}.png"
        base.resize((px, px), Image.Resampling.LANCZOS).save(iconset / name)

run(["iconutil", "-c", "icns", str(iconset), "-o", str(root / "build/DTAtoCSV.icns")], check=True)
