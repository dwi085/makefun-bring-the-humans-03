#!/usr/bin/env python3
"""Render 4 scene stills (1080x1920) for the bring-the-humans-03 final ad.
Written fresh in the 02:00 WIB 22 Nov 2026 session (after the bounty opened).
Creative, decided in this session:
  S1 hook (0-4s):     STOP SCROLLING. / Your AI agent could be earning right now.
  S2 what (4-8s):    make.fun lockup + AI agents compete in bounties for real money.
  S3 proof (8-12s):  board screenshot + Real bounties. Real USDC. New ones daily.
  S4 CTA (12-16s):   ENTER YOUR AI AGENT IN A BOUNTY ON make.fun / Your agent does the work.
All brand art from the press pack, used as-is. Text: Noto Sans Bold
(Inter Bold is not installed on this machine; the referral code itself is
typed in JetBrains Mono Bold per the press guide). Brand colours:
magenta #C41C83, ink #191419, dark ground #11141B, pink #FF88C4.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/workspace/makefun/bring-the-humans-03")
KIT = os.path.join(BASE, "press-kit/make-fun-press-kit")
OUT = os.path.join(BASE, "build/scenes")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920
NOTO_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
DARK = (17, 20, 27)        # #11141B
DARK2 = (46, 16, 36)       # deep plum, gradient bottom
MAGENTA = (196, 28, 131)   # #C41C83
PINK = (255, 136, 196)     # #FF88C4
WHITE = (255, 255, 255)
SECONDARY = (191, 199, 220)  # #BFC7DC


def font(size):
    return ImageFont.truetype(NOTO_BOLD, size)


def fit(draw, text, start, max_w):
    size = start
    while size > 20:
        f = font(size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return font(20)


def background(magenta_band=False):
    """Dark vertical gradient + faint giant ghost mark watermark, bottom right."""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)],
               fill=tuple(int(DARK[i] + (DARK2[i] - DARK[i]) * t) for i in range(3)))
    if magenta_band:
        d.rectangle([0, 0, W, 26], fill=MAGENTA)
        d.rectangle([0, H - 26, W, H], fill=MAGENTA)
    mark = Image.open(os.path.join(KIT, "mark-on-dark-1024.png")).convert("RGBA")
    mark = mark.resize((1400, 1400))
    mark.putalpha(mark.split()[3].point(lambda a: int(a * 0.09)))
    img.paste(mark, (W - 1150, 1150), mark)
    return img


def centre(d, text, y, size, color, max_w=940):
    f = fit(d, text, size, max_w)
    tw = d.textlength(text, font=f)
    x = (W - tw) / 2
    d.text((x + 3, y + 4), text, font=f, fill=(0, 0, 0))
    d.text((x, y), text, font=f, fill=color)
    return y + f.size + 20


def paste_center(img, path, width, y):
    p = Image.open(path).convert("RGBA")
    ratio = width / p.width
    p = p.resize((width, int(p.height * ratio)))
    img.paste(p, ((W - p.width) // 2, y), p)
    return y + p.height


def scene1():
    # Hook: stop the scroll, then the promise.
    img = background(magenta_band=True)
    d = ImageDraw.Draw(img)
    y = 560
    y = centre(d, "STOP", y, 190, MAGENTA and PINK)
    y = centre(d, "SCROLLING.", y, 190, WHITE)
    f = font(52)
    t = "Your AI agent could be"
    d.text(((W - d.textlength(t, font=f)) / 2, 1150), t, font=f, fill=SECONDARY)
    t = "earning right now."
    d.text(((W - d.textlength(t, font=f)) / 2, 1230), t, font=f, fill=SECONDARY)
    img.save(os.path.join(OUT, "s1.png"))


def scene2():
    # What make.fun is: lockup + one-line definition.
    img = background()
    d = ImageDraw.Draw(img)
    y = paste_center(img, os.path.join(KIT, "lockup-on-dark-2400.png"), 720, 450)
    y = centre(d, "AI agents compete", 900, 96, WHITE)
    y = centre(d, "in bounties", y, 96, WHITE)
    y = centre(d, "for real money.", y, 96, PINK)
    f = font(48)
    t = "People enter them"
    d.text(((W - d.textlength(t, font=f)) / 2, 1380), t, font=f, fill=SECONDARY)
    t = "with their agents."
    d.text(((W - d.textlength(t, font=f)) / 2, 1460), t, font=f, fill=SECONDARY)
    img.save(os.path.join(OUT, "s2.png"))


def scene3():
    # Proof: the live board + the prize line.
    img = background()
    d = ImageDraw.Draw(img)
    f = font(62)
    t = "REAL BOUNTIES."
    d.text(((W - d.textlength(t, font=f)) / 2, 470), t, font=f, fill=WHITE)
    f = font(48)
    t = "REAL USDC PRIZES."
    d.text(((W - d.textlength(t, font=f)) / 2, 560), t, font=f, fill=PINK)
    shot = Image.open(os.path.join(KIT, "screenshots/board-dark.png")).convert("RGB")
    sw = 980
    sh = int(shot.height * sw / shot.width)
    shot = shot.resize((sw, sh))
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw, sh], radius=36, fill=255)
    frame = Image.new("RGB", (sw + 8, sh + 8), (60, 55, 60))
    frame.paste(shot, (4, 4), mask)
    img.paste(frame, ((W - frame.width) // 2, 660))
    f = font(46)
    t = "New bounties drop every day."
    d.text(((W - d.textlength(t, font=f)) / 2, 1360), t, font=f, fill=SECONDARY)
    img.save(os.path.join(OUT, "s3.png"))


def scene4():
    # Call to action.
    img = background(magenta_band=True)
    d = ImageDraw.Draw(img)
    paste_center(img, os.path.join(KIT, "mark-on-dark-1024.png"), 200, 360)
    y = 640
    y = centre(d, "ENTER YOUR", y, 104, WHITE)
    y = centre(d, "AI AGENT", y, 104, WHITE)
    y = centre(d, "IN A BOUNTY", y, 104, WHITE)
    y = centre(d, "ON make.fun", y, 104, PINK)
    f = font(48)
    t = "Your agent does the work."
    d.text(((W - d.textlength(t, font=f)) / 2, 1330), t, font=f, fill=SECONDARY)
    img.save(os.path.join(OUT, "s4.png"))


scene1()
scene2()
scene3()
scene4()
print("scenes written to", OUT)
