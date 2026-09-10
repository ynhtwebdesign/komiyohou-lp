# -*- coding: utf-8 -*-
"""生成したイラストを、LPに載せる形(WebP)に整える。
丸アイコンは周囲の余白を自前で切り落としてから正方形にする
（生成画像は余白が大きく、そのまま丸に入れると絵が小さすぎて読めない）。"""
import os, sys
from PIL import Image, ImageOps, ImageDraw, ImageChops

SRC = "_src"
ICONS = ["f-mikomi","f-shikomi","f-calendar","f-shiire","f-shukyaku","f-jikan",
         "k-tenki","k-youbi","k-kyuryo","k-event","k-gakko","k-sports","k-kisetsu","k-machi"]
CARDS = ["ba-ame","ba-matsuri","ba-tsukizue"]             # 導入後のお店 4:3
WIDE = ["m-herasu","m-urebi","m-nayami","m-zaisan"]        # メリットのカード 16:9

def trim_square(im, pad=0.10):
    rgb = im.convert("RGB")
    bg = Image.new("RGB", rgb.size, rgb.getpixel((4, 4)))       # 角の色＝地のクリーム
    diff = ImageChops.difference(rgb, bg).convert("L").point(lambda v: 255 if v > 28 else 0)
    box = diff.getbbox() or (0, 0, *rgb.size)
    x0, y0, x1, y1 = box
    side = int(max(x1 - x0, y1 - y0) * (1 + pad * 2))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # ⚠ 絵が画像の端に寄っていると、正方形が元画像からはみ出す。
    #    crop() ではみ出させると外側が黒で埋まるので(地域のイベントで一度これをやった)、
    #    はみ出さない範囲だけ切り取り、地のクリームを敷いた正方形の上に貼る。
    left, top = cx - side // 2, cy - side // 2
    canvas = Image.new("RGB", (side, side), rgb.getpixel((4, 4)))
    sx0, sy0 = max(left, 0), max(top, 0)
    sx1, sy1 = min(left + side, rgb.width), min(top + side, rgb.height)
    canvas.paste(rgb.crop((sx0, sy0, sx1, sy1)), (sx0 - left, sy0 - top))
    return canvas

def circle(im, d):
    im = im.resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    out = Image.new("RGB", (d, d), (255, 255, 255)); out.paste(im, (0, 0), m); return out

done = []
for n in ICONS:
    p = os.path.join(SRC, n + ".png")
    if not os.path.exists(p): continue
    sq = trim_square(Image.open(p))
    sq.resize((200, 200), Image.LANCZOS).save(n + ".webp", "WEBP", quality=90, method=6)
    done.append(n)
for n in CARDS:
    p = os.path.join(SRC, n + ".png")
    if not os.path.exists(p): continue
    ImageOps.fit(Image.open(p).convert("RGB"), (720, 540), Image.LANCZOS).save(n + ".webp", "WEBP", quality=90, method=6)

for n in WIDE:
    p = os.path.join(SRC, n + ".png")
    if not os.path.exists(p): continue
    ImageOps.fit(Image.open(p).convert("RGB"), (720, 405), Image.LANCZOS).save(n + ".webp", "WEBP", quality=90, method=6)

# 確認用シート：各アイコンを 実寸56px の丸 と 160px で並べる
if "--sheet" in sys.argv:
    cols, cw, ch = 7, 190, 250
    rows = (len(done) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rows * ch), (255, 255, 255))
    for i, n in enumerate(done):
        im = Image.open(n + ".webp")
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.paste(im.resize((160, 160), Image.LANCZOS), (x + 15, y + 8))
        sheet.paste(circle(im, 56), (x + 67, y + 180))
    sheet.save(os.path.join(SRC, "_sheet.png"))
print("アイコン", len(done), "枚 / カード", sum(os.path.exists(n + ".webp") for n in CARDS), "枚")
