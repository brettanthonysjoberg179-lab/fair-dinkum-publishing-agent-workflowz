#!/usr/bin/env python3
"""FDP covers (1600x2560) + thumbs (600x315) — eucalypt green + wattle gold.
Usage: python3 make_covers.py
Out: gumroad-covers/FDP-*.png, gumroad-thumbs/FDP-*.png
"""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont

GREEN, GOLD, CREAM, DARK = (14, 77, 46), (200, 138, 0), (248, 246, 238), (20, 30, 26)
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BOOKS = [
    ("FDP-AAW-001", "Aussie Agent\nWorkflowz", "Playbook", "12 AGENT WORKFLOWS · FLIPBOOK + PDF", "$49 AUD"),
    ("FDP-SOLO-002", "Solopreneur\nOS", "The Solo System", "ONE INBOX · ONE REVIEW · ONE MONEY DAY", "$29 AUD"),
    ("FDP-SKATE-003", "Skateboarding", "A Fair Dinkum Ride", "18 ERAS · CLAY WHEELS TO TOKYO 2020", "$29 AUD"),
    ("FDP-GRAF-004", "Graffiti", "Walls That Talk", "16 CHAPTERS · PHILLY 1967 TO INTERNET AGE", "$29 AUD"),
    ("FDP-BUNDLE-001", "Skate +\nGraffiti", "2-Pack Bundle", "TWO HISTORIES · ONE STREET · SAVE $13", "$45 AUD"),
]

def cover(sku, title, tagline, strap, price):
    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), GREEN)
    d = ImageDraw.Draw(img)
    for i in range(0, H, 8):  # subtle diagonal texture
        d.line([(0, i), (W, i + W // 6)], fill=(17, 88, 53), width=2)
    d.rectangle([0, 0, W, 260], fill=DARK)                       # top band
    d.rectangle([0, H - 420, W, H], fill=DARK)                   # bottom band
    d.rectangle([0, 300, W, 316], fill=GOLD)                     # gold rules
    d.rectangle([0, H - 436, W, H - 420], fill=GOLD)
    f_brand = ImageFont.truetype(SANS_B, 54)
    f_title = ImageFont.truetype(SERIF_B, 190)
    f_tag = ImageFont.truetype(SANS, 64)
    f_strap = ImageFont.truetype(SANS_B, 44)
    f_price = ImageFont.truetype(SERIF_B, 120)
    f_foot = ImageFont.truetype(SANS, 46)
    d.text((W // 2, 140), "FAIR DINKUM PUBLISHING", font=f_brand, fill=GOLD, anchor="mm")
    y = 700
    for line in title.split("\n"):
        d.text((W // 2, y), line, font=f_title, fill=CREAM, anchor="ma")
        y += 220
    d.text((W // 2, y + 40), tagline, font=f_tag, fill=GOLD, anchor="ma")
    # strap boxed centre
    bb = d.textbbox((0, 0), strap, font=f_strap)
    bw = bb[2] - bb[0] + 80
    d.rectangle([W // 2 - bw // 2, 1560, W // 2 + bw // 2, 1660], outline=GOLD, width=4)
    d.text((W // 2, 1610), strap, font=f_strap, fill=CREAM, anchor="mm")
    d.text((W // 2, H - 280), price, font=f_price, fill=GOLD, anchor="mm")
    d.text((W // 2, H - 140), "BRETT SJOBERG · ADELAIDE SA", font=f_foot, fill=CREAM, anchor="mm")
    return img

def thumb(sku, title_one_line, cover_img):
    W, H = 600, 315
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=GOLD)
    ch = cover_img.resize((197, 315), Image.LANCZOS)
    img.paste(ch, (0, 0))
    d.line([(197, 0), (197, H)], fill=GOLD, width=3)
    f_t = ImageFont.truetype(SERIF_B, 44)
    f_s = ImageFont.truetype(SANS_B, 26)
    f_b = ImageFont.truetype(SANS, 24)
    words, lines, cur = title_one_line.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f_t) < 340: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    y = 60
    for ln in lines[:3]:
        d.text((225, y), ln, font=f_t, fill=CREAM)
        y += 56
    d.text((225, y + 8), "FAIR DINKUM PUBLISHING", font=f_s, fill=GOLD)
    d.text((225, y + 44), "Flipbook + PDF · Instant download", font=f_b, fill=(170, 180, 175))
    return img

if __name__ == "__main__":
    os.makedirs("gumroad-covers", exist_ok=True)
    os.makedirs("gumroad-thumbs", exist_ok=True)
    for sku, title, tag, strap, price in BOOKS:
        one = title.replace("\n", " ")
        c = cover(sku, title, tag, strap, price)
        c.save(f"gumroad-covers/{sku}.png", optimize=True)
        t = thumb(sku, one, c)
        t.save(f"gumroad-thumbs/{sku}.png", optimize=True)
        print(sku, "cover", os.path.getsize(f"gumroad-covers/{sku}.png") // 1024, "KB / thumb",
              os.path.getsize(f"gumroad-thumbs/{sku}.png") // 1024, "KB")
    print("Done.")
