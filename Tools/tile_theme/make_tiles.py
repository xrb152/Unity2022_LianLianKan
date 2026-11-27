# -*- coding: utf-8 -*-
"""
「闲舟静泛清波」牌面主题生成器。

36 张 256x256 满幅卡片：玉白底 + 深青外框 + 淡青内框 + 水乡图标。
图标是扁平风，统一深青描边，配色跟主界面/游戏内背景同源。

输出：Assets/Resources/TileThemes/xianzhou/0.png ~ 35.png

用法：python Tools/tile_theme/make_tiles.py
"""
import math
import os

from PIL import Image, ImageDraw

S, SS = 256, 4
W = S * SS
LW = 7.0
OW = LW * SS

INK = (28, 58, 56, 255)
CREAM = (250, 245, 234, 255)
CREAM_D = (222, 210, 188, 255)
TEAL = (64, 170, 154, 255)
TEAL_D = (34, 116, 104, 255)
TEAL_L = (170, 228, 216, 255)
BLUE = (92, 156, 178, 255)
BLUE_D = (52, 106, 130, 255)
SAND = (244, 198, 120, 255)
SAND_D = (206, 152, 72, 255)
CORAL = (238, 140, 132, 255)
CORAL_D = (198, 96, 92, 255)
JADE = (124, 190, 134, 255)
JADE_D = (76, 142, 90, 255)
GOLD = (246, 200, 92, 255)
WHITE = (255, 255, 255, 255)
SILVER = (224, 234, 236, 255)
PINK = (246, 178, 200, 255)
PINK_L = (253, 222, 232, 255)
PINK_D = (204, 118, 150, 255)
WOOD = (238, 220, 190, 255)
WOOD_D = (196, 166, 124, 255)


def X(v):
    return v * SS


def new_canvas():
    return Image.new("RGBA", (W, W), (0, 0, 0, 0))


def ell(d, cx, cy, rx, ry, fill, ow=OW):
    d.ellipse([X(cx - rx) - ow, X(cy - ry) - ow, X(cx + rx) + ow, X(cy + ry) + ow], fill=INK)
    d.ellipse([X(cx - rx), X(cy - ry), X(cx + rx), X(cy + ry)], fill=fill)


def poly(d, pts, fill, ow=OW):
    p = [(X(a), X(b)) for a, b in pts]
    d.line(p + [p[0]], fill=INK, width=int(ow * 2), joint="curve")
    d.polygon(p, fill=fill)


def rrect(d, x0, y0, x1, y1, r, fill, ow=OW):
    d.rounded_rectangle([X(x0) - ow, X(y0) - ow, X(x1) + ow, X(y1) + ow], radius=X(r) + ow, fill=INK)
    d.rounded_rectangle([X(x0), X(y0), X(x1), X(y1)], radius=X(r), fill=fill)


def line(d, pts, color, w=12, caps=True):
    p = [(X(a), X(b)) for a, b in pts]
    ww = max(1, int(X(w)))
    d.line(p, fill=color, width=ww, joint="curve")
    if caps:
        for (a, b) in (p[0], p[-1]):
            d.ellipse([a - ww / 2, b - ww / 2, a + ww / 2, b + ww / 2], fill=color)


def arc(d, cx, cy, r, a0, a1, color, w=12):
    bbox = [X(cx - r), X(cy - r), X(cx + r), X(cy + r)]
    d.arc(bbox, a0, a1, fill=INK, width=int(X(w + 2 * LW)))
    d.arc(bbox, a0, a1, fill=color, width=int(X(w)))


def pieslice(d, x0, y0, x1, y1, a0, a1, fill):
    d.pieslice([X(x0) - OW, X(y0) - OW, X(x1) + OW, X(y1) + OW], a0, a1, fill=INK)
    d.pieslice([X(x0), X(y0), X(x1), X(y1)], a0, a1, fill=fill)


def petal(cx, cy, ang, L, Wd, n=20):
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        s = math.sin(math.pi * t) * Wd
        x, y = cx + ca * L * t, cy + sa * L * t
        left.append((x + px * s, y + py * s))
        right.append((x - px * s, y - py * s))
    return left + right[::-1]


def sine_pts(x0, x1, y, amp, periods, n=60, start=0.0):
    return [(x0 + (x1 - x0) * i / n, y + amp * math.sin(2 * math.pi * periods * i / n + start))
            for i in range(n + 1)]


# ---------------- 水乡图标 ----------------
def i_lotus(d):
    for i in range(5):
        poly(d, petal(128, 158, math.radians(i * 72 - 90), 86, 39), PINK_L)
    for i in range(3):
        poly(d, petal(128, 158, math.radians(i * 120 - 90), 64, 31), PINK)
    ell(d, 128, 160, 17, 14, GOLD)


def i_pod(d):
    line(d, [(128, 54), (128, 98)], JADE_D, 9)
    ell(d, 128, 150, 50, 54, JADE)
    for (px, py) in [(106, 128), (128, 120), (150, 128), (114, 154), (142, 154), (128, 176)]:
        ell(d, px, py, 8, 8, JADE_D, ow=X(2))


def i_pad(d):
    pieslice(d, 54, 58, 202, 202, 8, 352, TEAL)
    for i in range(9):
        a = math.radians(10 + (340) * i / 8)
        line(d, [(128, 130), (128 + math.cos(a) * 70, 130 + math.sin(a) * 68)], TEAL_D, 5)
    ell(d, 128, 130, 11, 10, TEAL_D, ow=X(2))


def i_root(d):
    for i in range(3):
        x = 70 + i * 44
        ell(d, x, 128, 25, 21, WOOD)
        if i < 2:
            line(d, [(x + 22, 118), (x + 22, 138)], WOOD_D, 6)


def i_boat(d):
    poly(d, [(44, 100), (72, 172), (184, 172), (212, 100), (176, 118), (128, 142), (80, 118)], WOOD)
    line(d, [(92, 146), (164, 146)], WOOD_D, 8)
    line(d, [(50, 103), (206, 103)], WHITE, 5)


def i_oar(d):
    line(d, [(88, 54), (140, 160)], WOOD, 11)
    ell(d, 84, 46, 18, 13, WOOD_D)
    ell(d, 152, 186, 24, 32, WOOD)


def i_wave(d):
    for i, y in enumerate((100, 130, 160)):
        line(d, sine_pts(48, 208, y, 13, 1.5, 40), TEAL if i % 2 == 0 else TEAL_L, 11)


def i_ripple(d):
    for i, r in enumerate((34, 58, 82)):
        arc(d, 128, 128, r, 0, 360, TEAL_L if i else TEAL, 6)


def i_fish(d):
    poly(d, [(76, 128), (50, 100), (50, 156)], TEAL)
    ell(d, 132, 128, 52, 34, TEAL)
    ell(d, 158, 118, 7, 7, INK, ow=X(1))
    arc(d, 130, 128, 24, 300, 60, TEAL_L, 5)


def i_dragonfly(d):
    for (dx, dy, rx, ry) in [(-44, -14, 42, 15), (44, -14, 42, 15), (-38, 20, 36, 13), (38, 20, 36, 13)]:
        ell(d, 128 + dx, 122 + dy, rx, ry, TEAL_L, ow=X(2.5))
    ell(d, 128, 126, 11, 38, TEAL)
    ell(d, 128, 78, 15, 13, TEAL_D)


def i_fly(d):
    poly(d, petal(128, 128, math.radians(-142), 62, 26), PINK_L)
    poly(d, petal(128, 128, math.radians(-38), 62, 26), PINK_L)
    poly(d, petal(128, 128, math.radians(142), 48, 22), PINK)
    poly(d, petal(128, 128, math.radians(38), 48, 22), PINK)
    line(d, [(128, 80), (128, 176)], INK, 7)


def i_frog(d):
    ell(d, 128, 156, 62, 42, JADE)
    ell(d, 96, 108, 21, 21, JADE, ow=X(3))
    ell(d, 160, 108, 21, 21, JADE, ow=X(3))
    ell(d, 96, 108, 8, 8, INK, ow=X(1))
    ell(d, 160, 108, 8, 8, INK, ow=X(1))
    arc(d, 128, 162, 26, 20, 160, JADE_D, 6)


def i_firefly(d):
    for (dx, dy) in [(-22, 108), (22, 108)]:
        ell(d, 128 + dx, dy, 24, 11, TEAL_L, ow=X(2))
    ell(d, 128, 138, 18, 26, TEAL_D)
    ell(d, 128, 176, 22, 22, GOLD, ow=X(3))


def i_reed(d):
    for (bx, top, lean) in [(88, 64, -10), (128, 48, 0), (168, 62, 10)]:
        line(d, [(bx, 216), (bx + lean, top)], JADE_D, 7)
        ell(d, bx + lean, top - 6, 8, 20, SAND, ow=X(2.5))


def i_fan(d):
    pieslice(d, 44, 58, 212, 232, 200, 340, SAND)
    line(d, [(128, 192), (140, 228)], SAND_D, 11)


def i_lantern(d):
    line(d, [(128, 40), (128, 64)], INK, 6)
    rrect(d, 92, 62, 164, 74, 5, SAND_D, ow=X(2.5))
    ell(d, 128, 130, 48, 50, CORAL)
    for y in (112, 130, 148):
        line(d, [(86, y), (170, y)], CORAL_D, 4)
    rrect(d, 92, 176, 164, 188, 5, SAND_D, ow=X(2.5))
    line(d, [(128, 188), (128, 214)], GOLD, 5)


def i_teapot(d):
    ell(d, 130, 142, 52, 42, TEAL)
    rrect(d, 108, 82, 152, 102, 9, TEAL, ow=X(3))
    ell(d, 130, 78, 7, 7, TEAL_D, ow=X(2))
    line(d, [(172, 126), (204, 106)], TEAL_D, 9)
    arc(d, 84, 132, 24, 250, 110, TEAL_D, 9)


def i_basket(d):
    poly(d, [(76, 100), (180, 100), (166, 196), (90, 196)], SAND)
    for i in range(3):
        line(d, [(84 + i * 2, 124 + i * 24), (172 - i * 2, 124 + i * 24)], SAND_D, 4)
    arc(d, 128, 100, 42, 200, 340, SAND_D, 7)


def i_umbrella(d):
    pieslice(d, 42, 62, 214, 194, 180, 360, CORAL)
    for i in range(5):
        a = math.radians(180 + i * 45)
        line(d, [(128, 128), (128 + math.cos(a) * 84, 128 + math.sin(a) * 64)], CORAL_D, 4)
    line(d, [(128, 128), (128, 208)], WOOD_D, 7)


def i_bridge(d):
    arc(d, 128, 150, 70, 180, 360, SILVER, 22)
    rrect(d, 44, 150, 66, 198, 7, SILVER, ow=X(3))
    rrect(d, 190, 150, 212, 198, 7, SILVER, ow=X(3))
    for x, y in [(88, 128), (128, 112), (168, 128)]:
        line(d, [(x, y), (x, 150)], SILVER, 5)


def i_tile(d):
    # 瓦：两排交错的半圆瓦当。单道拱弧会跟"雨"里的云、跟石桥撞脸
    for cy, xs, col, rim in ((200, (78, 128, 178), CORAL, CORAL_D),
                             (168, (103, 153), CORAL_D, CORAL)):
        for cx in xs:
            pieslice(d, cx - 30, cy - 30, cx + 30, cy + 30, 180, 360, col)
            arc(d, cx, cy, 21, 190, 350, rim, 5)


def i_caltrop(d):
    poly(d, [(128, 64), (162, 128), (128, 196), (94, 128)], JADE)
    line(d, [(128, 70), (128, 190)], JADE_D, 5)


def i_dew(d):
    poly(d, [(120, 58), (162, 130), (152, 176), (88, 176), (78, 130)], TEAL)
    ell(d, 100, 116, 12, 16, WHITE, ow=X(1))
    # 一颗容易被当成"水滴"，补一颗小的才读得出是"露"
    ell(d, 186, 168, 21, 21, TEAL_L, ow=X(2))
    ell(d, 179, 161, 6, 6, WHITE, ow=X(1))


def i_moon(d):
    ell(d, 128, 134, 62, 62, SAND)
    for (px, py, r) in [(196, 78, 9), (72, 68, 6), (206, 160, 5)]:
        poly(d, [(px, py - r * 2), (px + r * 0.6, py), (px, py + r * 2), (px - r * 0.6, py)], WHITE, ow=X(1.5))


def i_sun(d):
    for i in range(8):
        a = math.radians(i * 45)
        line(d, [(128 + math.cos(a) * 78, 128 + math.sin(a) * 78),
                 (128 + math.cos(a) * 104, 128 + math.sin(a) * 104)], SAND_D, 8)
    ell(d, 128, 128, 56, 56, SAND)


def i_cloud(d):
    ell(d, 96, 138, 30, 26, WHITE, ow=X(3))
    ell(d, 132, 120, 38, 34, WHITE, ow=X(3))
    ell(d, 172, 140, 28, 24, WHITE, ow=X(3))
    rrect(d, 74, 138, 192, 168, 13, WHITE, ow=X(3))


def i_rain(d):
    # 三个圆如果各自描边，看着像一排蘑菇；先铺一遍"描边色"的整体轮廓，再铺云体
    bumps = [(128, 106, 40, 32), (92, 120, 27, 22), (166, 120, 27, 22)]
    for (cx, cy, rx, ry) in bumps:
        ell(d, cx, cy, rx + 4, ry + 4, INK)
    rrect(d, 62, 118, 194, 156, 18, INK)
    for (cx, cy, rx, ry) in bumps:
        ell(d, cx, cy, rx, ry, BLUE)
    rrect(d, 66, 122, 190, 152, 14, BLUE)
    for x in (96, 128, 160):
        line(d, [(x, 158), (x - 6, 190)], BLUE_D, 7)


def i_bird(d):
    # 身子用淡青、颈头用深青：纯白描边在玉白底板上等于没有
    ell(d, 124, 142, 42, 26, TEAL_L)
    ell(d, 116, 136, 24, 14, WHITE, ow=X(1))
    line(d, [(148, 126), (180, 96)], TEAL, 9)
    ell(d, 188, 88, 13, 11, TEAL, ow=X(2.5))
    ell(d, 192, 85, 4, 4, WHITE, ow=X(1))
    line(d, [(199, 86), (217, 90)], GOLD, 5)
    line(d, [(110, 160), (106, 200)], GOLD, 5)
    line(d, [(132, 162), (134, 204)], GOLD, 5)


def i_snail(d):
    arc(d, 128, 140, 66, 0, 360, SAND, 14)
    arc(d, 128, 140, 42, 0, 360, SAND_D, 11)
    arc(d, 128, 140, 20, 0, 360, SAND, 9)


def i_shell(d):
    pieslice(d, 54, 78, 202, 222, 180, 360, PINK_L)
    for i in range(5):
        a = math.radians(190 + i * 40)
        line(d, [(128, 178), (128 + math.cos(a) * 68, 178 + math.sin(a) * 68)], PINK, 4)


def i_net(d):
    for i in range(4):
        line(d, [(74 + i * 22, 74), (74 + i * 22, 192)], SAND, 4)
        line(d, [(74, 74 + i * 30), (184, 74 + i * 30)], SAND, 4)
    ell(d, 74, 72, 8, 8, CORAL, ow=X(2))
    ell(d, 184, 72, 8, 8, CORAL, ow=X(2))


def i_raft(d):
    for i in range(4):
        rrect(d, 52 + i * 34, 98, 82 + i * 34, 176, 8, WOOD, ow=X(3))
    line(d, [(60, 122), (196, 122)], WOOD_D, 5)
    line(d, [(60, 152), (196, 152)], WOOD_D, 5)


def i_bud(d):
    line(d, [(128, 158), (128, 216)], JADE_D, 8)
    poly(d, petal(128, 158, math.radians(-90), 92, 34), PINK_L)
    poly(d, petal(128, 158, math.radians(-120), 66, 22), PINK)
    poly(d, petal(128, 158, math.radians(-60), 66, 22), PINK)


def i_grass(d):
    for (x, bend) in [(86, -26), (128, 0), (170, 26)]:
        pts = [(x, 214)]
        for t in (0.34, 0.67, 1.0):
            pts.append((x + bend * t + 10 * math.sin(t * 5), 214 - 116 * t))
        line(d, pts, JADE, 9)


def i_pebble(d):
    poly(d, [(78, 166), (72, 140), (94, 124), (128, 130), (140, 154), (122, 176)], SILVER)
    poly(d, [(142, 184), (138, 158), (162, 148), (186, 162), (184, 184), (160, 190)], SILVER)
    ell(d, 152, 112, 21, 15, TEAL_L)


def i_coin(d):
    ell(d, 128, 128, 62, 62, GOLD)
    rrect(d, 108, 108, 148, 148, 4, CREAM, ow=X(3))


ICONS = [
    ("0", i_lotus), ("1", i_pod), ("2", i_pad), ("3", i_root),
    ("4", i_boat), ("5", i_oar), ("6", i_wave), ("7", i_ripple),
    ("8", i_fish), ("9", i_dragonfly), ("10", i_fly), ("11", i_frog),
    ("12", i_firefly), ("13", i_reed), ("14", i_fan), ("15", i_lantern),
    ("16", i_teapot), ("17", i_basket), ("18", i_umbrella), ("19", i_bridge),
    ("20", i_tile), ("21", i_caltrop), ("22", i_dew), ("23", i_moon),
    ("24", i_sun), ("25", i_cloud), ("26", i_rain), ("27", i_bird),
    ("28", i_snail), ("29", i_shell), ("30", i_net), ("31", i_raft),
    ("32", i_bud), ("33", i_grass), ("34", i_pebble), ("35", i_coin),
]

OUT = "Assets/Resources/TileThemes/xianzhou"


def plate():
    c = Image.new("RGBA", (W, W), CREAM)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([X(10), X(10), X(246), X(246)], radius=X(30),
                        outline=INK, width=int(X(6)))
    d.rounded_rectangle([X(24), X(24), X(232), X(232)], radius=X(20),
                        outline=TEAL_L, width=int(X(3)))
    return c.resize((S, S), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs("Temp", exist_ok=True)
    pl = plate()
    pl.save("Temp/tile_plate_preview.png")
    ICON = 196
    off = (S - ICON) // 2
    for name, fn in ICONS:
        c = new_canvas()
        d = ImageDraw.Draw(c)
        fn(d)
        icon = c.resize((ICON, ICON), Image.LANCZOS)
        out = pl.copy()
        out.alpha_composite(icon, (off, off))
        out.save(os.path.join(OUT, name + ".png"))
    print("生成 %d 张牌面（含底板）-> %s" % (len(ICONS), OUT))

    cols, rows, cell = 6, 6, 112
    sheet = Image.new("RGB", (cols * cell, rows * cell), (236, 238, 240))
    for k, (name, _) in enumerate(ICONS):
        im = Image.open(os.path.join(OUT, name + ".png")).convert("RGBA")
        im.thumbnail((cell - 8, cell - 8), Image.LANCZOS)
        x, y = (k % cols) * cell, (k // cols) * cell
        sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2), im)
    sheet.save("Temp/sheet_xianzhou.png")

    demo = Image.new("RGB", (cell * 6, cell * 2), (100, 176, 168))
    for k in range(12):
        im = Image.open(os.path.join(OUT, ICONS[k][0] + ".png")).convert("RGBA").resize((cell - 2, cell - 2), Image.LANCZOS)
        x, y = (k % 6) * cell, (k // 6) * cell
        demo.paste(im, (x + 1, y + 1), im)
    demo.save("Temp/sheet_xianzhou_onplate.png")
    print("预览 -> Temp/sheet_xianzhou.png")


if __name__ == "__main__":
    main()
