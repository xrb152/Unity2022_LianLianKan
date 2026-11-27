import math, os
from PIL import Image, ImageDraw

S, SS = 256, 4
W = S * SS
LW = 7.0
OW = LW * SS

INK    = (34, 48, 63, 255)
CREAM  = (251, 243, 228, 255)
CREAM_D= (232, 216, 188, 255)
TEAL   = (47, 163, 155, 255)
TEAL_D = (31, 116, 110, 255)
TEAL_L = (150, 219, 210, 255)
BLUE   = (58, 124, 168, 255)
BLUE_D = (32, 78, 110, 255)
SAND   = (242, 200, 121, 255)
SAND_D = (214, 160, 79, 255)
CORAL  = (232, 115, 90, 255)
CORAL_D= (192, 80, 62, 255)
JADE   = (111, 191, 115, 255)
JADE_D = (70, 142, 84, 255)
GOLD   = (245, 194, 66, 255)
WHITE  = (255, 255, 255, 255)
SILVER = (222, 231, 238, 255)

def X(v): return v * SS

def new_canvas(): return Image.new("RGBA", (W, W), (0, 0, 0, 0))

def ell(d, cx, cy, rx, ry, fill, ow=OW):
    d.ellipse([X(cx-rx)-ow, X(cy-ry)-ow, X(cx+rx)+ow, X(cy+ry)+ow], fill=INK)
    d.ellipse([X(cx-rx), X(cy-ry), X(cx+rx), X(cy+ry)], fill=fill)

def poly(d, pts, fill, ow=OW):
    p = [(X(a), X(b)) for a, b in pts]
    d.line(p + [p[0]], fill=INK, width=int(ow*2), joint="curve")
    d.polygon(p, fill=fill)

def rrect(d, x0, y0, x1, y1, r, fill, ow=OW):
    d.rounded_rectangle([X(x0)-ow, X(y0)-ow, X(x1)+ow, X(y1)+ow], radius=X(r)+ow, fill=INK)
    d.rounded_rectangle([X(x0), X(y0), X(x1), X(y1)], radius=X(r), fill=fill)

def line(d, pts, color, w=12, caps=True):
    p = [(X(a), X(b)) for a, b in pts]
    ww = max(1, int(X(w)))
    d.line(p, fill=color, width=ww, joint="curve")
    if caps:
        for (a, b) in (p[0], p[-1]):
            d.ellipse([a-ww/2, b-ww/2, a+ww/2, b+ww/2], fill=color)

def stroke(d, pts, color, w=12):
    line(d, pts, INK, w + 2*LW)
    line(d, pts, color, w)

def arc(d, cx, cy, r, a0, a1, color, w=12):
    bbox = [X(cx-r), X(cy-r), X(cx+r), X(cy+r)]
    d.arc(bbox, a0, a1, fill=INK, width=int(X(w + 2*LW)))
    d.arc(bbox, a0, a1, fill=color, width=int(X(w)))

def pieslice(d, x0, y0, x1, y1, a0, a1, fill):
    d.pieslice([X(x0)-OW, X(y0)-OW, X(x1)+OW, X(y1)+OW], a0, a1, fill=INK)
    d.pieslice([X(x0), X(y0), X(x1), X(y1)], a0, a1, fill=fill)

def petal(cx, cy, ang, L, Wd, n=20):
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    left, right = [], []
    for i in range(n+1):
        t = i / n
        s = math.sin(math.pi * t) * Wd
        x, y = cx + ca*L*t, cy + sa*L*t
        left.append((x + px*s, y + py*s))
        right.append((x - px*s, y - py*s))
    return left + right[::-1]

def star(cx, cy, ro, ri, ang0=-90, n=5):
    pts = []
    for i in range(n*2):
        a = math.radians(ang0 + i*180.0/n)
        r = ro if i % 2 == 0 else ri
        pts.append((cx + math.cos(a)*r, cy + math.sin(a)*r))
    return pts

def wedge(d, cx, cy, r, a0, a1, fill, n=48):
    pts = [(cx, cy)]
    for i in range(n+1):
        a = math.radians(a0 + (a1-a0)*i/n)
        pts.append((cx + math.cos(a)*r, cy + math.sin(a)*r))
    poly(d, pts, fill)

def sine_pts(x0, x1, y, amp, periods, n=60, start=0.0):
    out = []
    for i in range(n+1):
        t = i/n
        out.append((x0 + (x1-x0)*t, y + amp*math.sin(2*math.pi*periods*t + start)))
    return out

def highlight(d, cx, cy, r, a0, a1, w=9, color=(255, 255, 255, 170)):
    arc_bbox = [X(cx-r), X(cy-r), X(cx+r), X(cy+r)]
    d.arc(arc_bbox, a0, a1, fill=color, width=int(X(w)))

# ---------------- icons ----------------
def i_shell(d):
    pts = []
    for i in range(61):
        a = math.radians(198 + (342-198)*i/60)
        r = 108 * (1 + 0.055*math.cos(7*(a - math.radians(198))))
        pts.append((128 + math.cos(a)*r, 198 + math.sin(a)*r))
    pts.append((128, 198))
    poly(d, pts, SAND)
    for a in range(-152, -10, 26):
        line(d, [(128, 198), (128 + math.cos(math.radians(a))*96, 198 + math.sin(math.radians(a))*96)], SAND_D, 7)
    rrect(d, 108, 178, 148, 212, 16, CREAM)

def i_starfish(d):
    poly(d, star(128, 128, 94, 40), SAND)
    for a in (-90, -18, 54, 126, 198):
        r = math.radians(a); ell(d, 128+math.cos(r)*52, 128+math.sin(r)*52, 9, 9, SAND_D, ow=0)

def i_fish(d):
    poly(d, [(172, 128), (214, 92), (214, 164)], TEAL_D)
    ell(d, 122, 128, 64, 46, TEAL)
    ell(d, 98, 114, 13, 13, WHITE, ow=5)
    ell(d, 98, 114, 6, 6, INK, ow=0)
    arc(d, 128, 128, 34, 300, 60, TEAL_L, 8)

def i_crab(d):
    for s in (-1, 1):
        for k, dy in enumerate((0, 22, 44)):
            line(d, [(128 + s*56, 140 + dy - 10), (128 + s*96, 148 + dy)], CORAL_D, 11)
    line(d, [(104, 118), (98, 92)], CORAL_D, 10)
    line(d, [(152, 118), (158, 92)], CORAL_D, 10)
    ell(d, 98, 86, 13, 13, WHITE, ow=5); ell(d, 98, 86, 6, 6, INK, ow=0)
    ell(d, 158, 86, 13, 13, WHITE, ow=5); ell(d, 158, 86, 6, 6, INK, ow=0)
    ell(d, 128, 144, 62, 44, CORAL)
    ell(d, 52, 122, 26, 20, CORAL); ell(d, 204, 122, 26, 20, CORAL)

def i_boat(d):
    line(d, [(128, 44), (128, 162)], INK, 9)
    poly(d, [(120, 56), (120, 152), (62, 152)], CREAM)
    poly(d, [(138, 72), (138, 152), (196, 152)], CORAL)
    poly(d, [(44, 164), (212, 164), (184, 204), (72, 204)], BLUE_D)

def i_palm(d):
    stroke(d, [(118, 206), (132, 160), (124, 112)], SAND_D, 17)
    for a in (-160, -120, -60, -20, 200):
        poly(d, petal(126, 106, math.radians(a), 78, 20), JADE)
    ell(d, 112, 114, 10, 10, SAND_D, ow=5)
    ell(d, 142, 112, 10, 10, SAND_D, ow=5)

def i_sun(d):
    for a in range(0, 360, 45):
        r = math.radians(a)
        line(d, [(128+math.cos(r)*72, 128+math.sin(r)*72), (128+math.cos(r)*98, 128+math.sin(r)*98)], GOLD, 13)
    ell(d, 128, 128, 58, 58, GOLD)
    highlight(d, 128, 128, 58, 200, 250)

def i_moon(d):
    pts = []
    for i in range(31):
        a = math.radians(58 + (302-58)*i/30)
        pts.append((138 + math.cos(a)*84, 128 + math.sin(a)*84))
    for i in range(31):
        a = math.radians(302 + (58-302)*i/30)
        pts.append((112 + math.cos(a)*70, 120 + math.sin(a)*70))
    poly(d, pts, GOLD)

def i_cloud(d):
    rrect(d, 58, 144, 198, 176, 26, CREAM)
    ell(d, 98, 144, 40, 38, CREAM)
    ell(d, 142, 128, 50, 48, CREAM)
    ell(d, 182, 146, 34, 32, CREAM)

def i_wave(d):
    stroke(d, sine_pts(48, 208, 118, 16, 1.5), TEAL_L, 15)
    stroke(d, sine_pts(48, 208, 156, 18, 1.5), TEAL, 15)
    stroke(d, sine_pts(48, 208, 194, 16, 1.5), BLUE, 15)

def i_mountain(d):
    poly(d, [(42, 194), (118, 62), (194, 194)], BLUE)
    poly(d, [(100, 194), (168, 92), (236, 194)], TEAL_D)
    poly(d, [(100, 100), (118, 62), (136, 100), (118, 112)], CREAM)
    line(d, [(36, 196), (220, 196)], INK, 8)

def i_compass(d):
    ell(d, 128, 128, 86, 86, BLUE_D)
    ell(d, 128, 128, 62, 62, CREAM)
    poly(d, [(128, 74), (146, 128), (110, 128)], CORAL)
    poly(d, [(128, 182), (146, 128), (110, 128)], BLUE)
    ell(d, 128, 128, 9, 9, GOLD, ow=5)

def i_chest(d):
    rrect(d, 54, 124, 202, 200, 10, SAND_D)
    pieslice(d, 54, 82, 202, 166, 180, 360, SAND)
    for x in (80, 156):
        rrect(d, x, 82, x+22, 200, 6, GOLD)
    rrect(d, 112, 138, 144, 174, 8, GOLD)
    ell(d, 128, 150, 6, 8, INK, ow=0)

def i_jade(d):
    ell(d, 128, 120, 74, 74, JADE)
    ell(d, 128, 120, 34, 34, CREAM)
    stroke(d, [(128, 194), (128, 216)], CORAL, 9)
    ell(d, 128, 200, 9, 9, CORAL_D, ow=5)
    highlight(d, 128, 120, 74, 190, 240, 10)

def i_bamboo(d):
    for x, h in ((78, 150), (118, 172), (158, 138)):
        rrect(d, x, 210-h, x+26, 210, 12, JADE)
        for y in (210-h+40, 210-h+86):
            line(d, [(x+2, y), (x+24, y)], JADE_D, 5)
    poly(d, petal(150, 64, math.radians(-150), 46, 14), JADE_D)

def i_pine(d):
    rrect(d, 118, 168, 138, 208, 6, SAND_D)
    poly(d, [(128, 42), (186, 108), (70, 108)], JADE_D)
    poly(d, [(128, 76), (198, 150), (58, 150)], JADE)
    poly(d, [(128, 112), (208, 190), (48, 190)], JADE_D)

def i_gourd(d):
    ell(d, 128, 158, 54, 50, SAND)
    ell(d, 128, 92, 32, 30, SAND)
    stroke(d, [(128, 66), (128, 50)], JADE_D, 9)
    line(d, [(96, 122), (160, 122)], CORAL, 7)
    highlight(d, 128, 158, 54, 200, 250, 8)

def i_sword(d):
    poly(d, [(128, 30), (150, 112), (128, 200), (106, 112)], SILVER)
    rrect(d, 90, 112, 166, 130, 9, GOLD)
    rrect(d, 116, 130, 140, 184, 9, CORAL_D)
    ell(d, 128, 196, 13, 13, GOLD, ow=6)

def i_scroll(d):
    rrect(d, 66, 76, 190, 180, 8, CREAM)
    for y in (104, 128, 152):
        line(d, [(86, y), (170, y)], CREAM_D, 8)
    rrect(d, 46, 62, 80, 194, 16, SAND)
    rrect(d, 176, 62, 210, 194, 16, SAND)

def i_lantern(d):
    ell(d, 128, 128, 64, 70, CORAL)
    rrect(d, 98, 44, 158, 68, 8, GOLD)
    rrect(d, 98, 188, 158, 212, 8, GOLD)
    for x in (100, 128, 156):
        arc(d, x, 128, 40, 250, 290, CORAL_D, 6)
    line(d, [(128, 212), (128, 238)], GOLD, 8)

def i_drum(d):
    rrect(d, 62, 84, 194, 180, 12, SAND_D)
    ell(d, 128, 84, 66, 20, SAND)
    ell(d, 128, 180, 66, 20, SAND_D)
    for x in (78, 178):
        ell(d, x, 132, 10, 10, GOLD, ow=5)

def i_lotus(d):
    for a in (-150, -110, -70, -30):
        poly(d, petal(128, 176, math.radians(a), 96, 26), CORAL)
    for a in (-125, -55):
        poly(d, petal(128, 176, math.radians(a), 70, 22), GOLD)
    ell(d, 128, 176, 20, 16, CREAM, ow=6)

def i_maple(d):
    poly(d, petal(126, 196, math.radians(-90), 104, 24), CORAL)
    poly(d, petal(126, 186, math.radians(-142), 78, 22), CORAL)
    poly(d, petal(130, 186, math.radians(-38), 78, 22), CORAL)
    poly(d, petal(126, 176, math.radians(-168), 56, 18), CORAL)
    poly(d, petal(130, 176, math.radians(-12), 56, 18), CORAL)
    line(d, [(128, 190), (128, 206)], CORAL_D, 8)

def i_mushroom(d):
    rrect(d, 104, 140, 152, 206, 12, CREAM)
    pieslice(d, 46, 66, 210, 186, 180, 360, CORAL)
    for cx, cy, r in ((92, 116, 15), (140, 100, 12), (172, 130, 10)):
        ell(d, cx, cy, r, r, CREAM, ow=5)

def i_gem(d):
    poly(d, [(128, 38), (198, 92), (176, 188), (80, 188), (58, 92)], TEAL)
    poly(d, [(128, 38), (128, 100), (58, 92)], TEAL_L)
    poly(d, [(128, 38), (198, 92), (128, 100)], TEAL_D)
    poly(d, [(58, 92), (80, 188), (128, 100)], TEAL_D)
    poly(d, [(198, 92), (176, 188), (128, 100)], TEAL_L)

def i_feather(d):
    poly(d, petal(120, 202, math.radians(-72), 160, 40), TEAL_L)
    line(d, [(120, 202), (152, 62)], TEAL_D, 7)
    for i in range(5):
        y = 176 - i*26
        line(d, [(126+i*4, y), (150+i*3, y-12)], TEAL_D, 5)

def i_conch(d):
    ell(d, 128, 128, 68, 64, SAND)
    pts = []
    for i in range(70):
        t = i/69
        a = math.radians(90 + 1080*t)
        r = 56*(1-t*0.92)
        pts.append((128 + math.cos(a)*r, 128 + math.sin(a)*r*0.92))
    line(d, pts, CORAL, 12)
    poly(d, petal(150, 148, math.radians(20), 54, 26), CORAL_D)

def i_anchor(d):
    stroke(d, [(128, 66), (128, 184)], BLUE_D, 16)
    stroke(d, [(86, 92), (170, 92)], BLUE_D, 14)
    ell(d, 128, 54, 18, 18, CREAM, ow=6)
    arc(d, 128, 150, 52, 22, 158, BLUE_D, 14)
    poly(d, [(76, 176), (100, 170), (86, 200)], BLUE_D)
    poly(d, [(180, 176), (156, 170), (170, 200)], BLUE_D)

def i_pearl(d):
    ell(d, 128, 120, 58, 58, CREAM)
    highlight(d, 128, 120, 58, 195, 245, 11, (255, 255, 255, 200))
    arc(d, 128, 172, 42, 20, 160, GOLD, 12)

def i_coral(d):
    stroke(d, [(128, 204), (128, 150)], CORAL, 15)
    stroke(d, [(128, 170), (96, 130), (92, 96)], CORAL, 13)
    stroke(d, [(128, 176), (162, 138), (166, 104)], CORAL, 13)
    stroke(d, [(128, 196), (100, 176), (80, 186)], CORAL, 12)
    for p in ((92, 90), (166, 98), (80, 180)):
        ell(d, p[0], p[1], 10, 10, CORAL_D, ow=4)

def i_hook(d):
    stroke(d, [(128, 62), (128, 148), (158, 184), (192, 152)], BLUE_D, 13)
    ell(d, 128, 50, 16, 16, CREAM, ow=6)

def i_net(d):
    rrect(d, 62, 62, 194, 194, 18, CREAM)
    for k in range(1, 4):
        v = 62 + k*33
        line(d, [(v, 66), (v, 190)], TEAL, 7)
        line(d, [(66, v), (190, v)], TEAL, 7)
    for p in ((52, 52), (204, 52), (52, 204), (204, 204)):
        ell(d, p[0], p[1], 11, 11, CORAL, ow=5)

def i_tent(d):
    poly(d, [(128, 54), (48, 196), (208, 196)], SAND)
    poly(d, [(128, 96), (98, 196), (158, 196)], CORAL_D)
    line(d, [(128, 54), (128, 196)], SAND_D, 7)

def i_fire(d):
    stroke(d, [(86, 196), (170, 172)], SAND_D, 14)
    stroke(d, [(86, 172), (170, 196)], SAND_D, 14)
    poly(d, petal(128, 176, math.radians(-90), 118, 40), CORAL)
    poly(d, petal(128, 176, math.radians(-90), 84, 26), GOLD)
    poly(d, petal(128, 178, math.radians(-90), 50, 15), CREAM)

def i_jelly(d):
    pieslice(d, 54, 62, 202, 178, 180, 360, TEAL_L)
    for x, ph in ((92, 0.0), (128, 1.2), (164, 2.4)):
        pts = []
        for i in range(21):
            t = i/20
            pts.append((x + 10*math.sin(2*math.pi*t*1.4 + ph), 176 + 56*t))
        stroke(d, pts, TEAL, 10)

def i_treasuremap(d):
    rrect(d, 52, 66, 204, 190, 10, CREAM)
    poly(d, [(204, 130), (204, 190), (144, 190)], CREAM_D)
    pts = [(76, 104), (100, 120), (96, 146), (128, 156), (150, 142)]
    for i in range(len(pts)-1):
        line(d, [pts[i], pts[i+1]], SAND_D, 6)
    line(d, [(160, 150), (180, 172)], CORAL, 8)
    line(d, [(180, 150), (160, 172)], CORAL, 8)

ICONS = [
    ("0",  i_shell), ("1",  i_starfish), ("2",  i_fish), ("3",  i_crab),
    ("4",  i_boat), ("5",  i_palm), ("6",  i_sun), ("7",  i_moon),
    ("8",  i_cloud), ("9",  i_wave), ("10", i_mountain), ("11", i_compass),
    ("12", i_chest), ("13", i_jade), ("14", i_bamboo), ("15", i_pine),
    ("16", i_gourd), ("17", i_sword), ("18", i_scroll), ("19", i_lantern),
    ("20", i_drum), ("21", i_lotus), ("22", i_maple), ("23", i_mushroom),
    ("24", i_gem), ("25", i_feather), ("26", i_conch), ("27", i_anchor),
    ("28", i_pearl), ("29", i_coral), ("30", i_hook), ("31", i_net),
    ("32", i_tent), ("33", i_fire), ("34", i_jelly), ("35", i_treasuremap),
]

OUT = "Assets/Resources/TileThemes/shanhai"

def plate():
    c = Image.new("RGBA", (W, W), CREAM)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([X(10), X(10), X(246), X(246)], radius=X(30),
                        outline=INK, width=int(X(6)))
    d.rounded_rectangle([X(24), X(24), X(232), X(232)], radius=X(20),
                        outline=CREAM_D, width=int(X(3)))
    return c.resize((S, S), Image.LANCZOS)

def main():
    os.makedirs(OUT, exist_ok=True)
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
    sheet = Image.new("RGB", (cols*cell, rows*cell), (236, 238, 240))
    for k, (name, _) in enumerate(ICONS):
        im = Image.open(os.path.join(OUT, name + ".png")).convert("RGBA")
        im.thumbnail((cell-8, cell-8), Image.LANCZOS)
        x, y = (k % cols)*cell, (k // cols)*cell
        sheet.paste(im, (x + (cell-im.width)//2, y + (cell-im.height)//2), im)
    sheet.save("Temp/sheet_shanhai.png")

    demo = Image.new("RGB", (cell*6, cell*2), (86, 148, 140))
    for k in range(12):
        im = Image.open(os.path.join(OUT, ICONS[k][0] + ".png")).convert("RGBA").resize((cell-2, cell-2), Image.LANCZOS)
        x, y = (k % 6)*cell, (k // 6)*cell
        demo.paste(im, (x+1, y+1), im)
    demo.save("Temp/sheet_shanhai_onplate.png")
    print("预览已生成")

if __name__ == "__main__":
    main()
