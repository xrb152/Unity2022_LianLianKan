# -*- coding: utf-8 -*-
"""
「闲舟静泛清波」主题背景（纯 PIL 绘制，无外部素材）

  Assets/Images/MainSence/back1.png  — 主界面，UI Image 拉伸铺满（PreserveAspect 0）
  Assets/Images/playUI/playBg.png    — 游戏内/帮助页，SpriteRenderer cover 裁切

风格：莲池水乡。粉紫天光 + 青绿水波 + 荷叶荷花 + 一叶小舟。

两张图必须保持 1920x1080 且同名 .meta 不动，否则场景里的引用要改。

用法：
  python Tools/bg/make_bg.py            # 预览 -> Temp/bg_new_*.png
  python Tools/bg/make_bg.py --apply    # 覆盖原图
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_W, OUT_H = 1920, 1080
SS = 2
W, H = OUT_W * SS, OUT_H * SS

MAIN_SRC = "Assets/Images/MainSence/back1.png"
PLAY_SRC = "Assets/Images/playUI/playBg.png"


# ---------------- 基础工具 ----------------
def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3))


def vgrad(w, h, stops):
    im = Image.new("RGB", (1, h))
    px = im.load()
    for y in range(h):
        t = y / max(1, h - 1)
        col = stops[-1][1]
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                col = mix(c0, c1, k)
                break
        px[0, y] = col
    return im.resize((w, h), Image.BICUBIC)


def glow(canvas, cx, cy, radius, rgb, peak=120):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=rgb + (peak,))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.62)))


def edge_shade(canvas, rgb=(18, 44, 44), top=0, bottom=0, left=0, right=0, alpha=150):
    """四边压暗，把视线圈在中间"""
    w, h = canvas.size
    if top > 0:
        g = ImageOps.invert(Image.linear_gradient("L")).resize((w, top), Image.BILINEAR)
        c = Image.new("RGBA", (w, top), rgb + (255,))
        c.putalpha(g.point(lambda v: int(v * alpha / 255)))
        canvas.alpha_composite(c, (0, 0))
    if bottom > 0:
        g = Image.linear_gradient("L").resize((w, bottom), Image.BILINEAR)
        c = Image.new("RGBA", (w, bottom), rgb + (255,))
        c.putalpha(g.point(lambda v: int(v * alpha / 255)))
        canvas.alpha_composite(c, (0, h - bottom))
    if left > 0:
        g = ImageOps.invert(Image.linear_gradient("L")).rotate(90, expand=True).resize((left, h), Image.BILINEAR)
        c = Image.new("RGBA", (left, h), rgb + (255,))
        c.putalpha(g.point(lambda v: int(v * alpha / 255)))
        canvas.alpha_composite(c, (0, 0))
    if right > 0:
        g = Image.linear_gradient("L").rotate(90, expand=True).resize((right, h), Image.BILINEAR)
        c = Image.new("RGBA", (right, h), rgb + (255,))
        c.putalpha(g.point(lambda v: int(v * alpha / 255)))
        canvas.alpha_composite(c, (w - right, 0))


def smooth1d(vals, sigma):
    if sigma <= 0:
        return vals
    r = int(sigma * 3)
    kernel = [math.exp(-(i * i) / (2 * sigma * sigma)) for i in range(-r, r + 1)]
    total = sum(kernel)
    kernel = [k / total for k in kernel]
    n = len(vals)
    out = []
    for i in range(n):
        acc = 0.0
        for j, k in enumerate(kernel):
            idx = min(n - 1, max(0, i + j - r))
            acc += vals[idx] * k
        out.append(acc)
    return out


def profile(ctrl, sigma=6.0, samples=900):
    """ctrl=[(x归一,y归一)] 升序；只覆盖控制点跨度，不会外推到全宽"""
    xs = [c[0] * W for c in ctrl]
    ys = [c[1] for c in ctrl]
    x0, x1 = xs[0], xs[-1]
    raw, pxs = [], []
    for i in range(samples + 1):
        x = x0 + (x1 - x0) * i / samples
        k = 0
        while k < len(xs) - 2 and x > xs[k + 1]:
            k += 1
        seg = (xs[k + 1] - xs[k]) or 1.0
        t = (x - xs[k]) / seg
        raw.append(ys[k] + (ys[k + 1] - ys[k]) * t)
        pxs.append(x)
    sm = smooth1d(raw, sigma)
    return [(pxs[i], sm[i] * H) for i in range(len(pxs))]


def fill_down(canvas, pts, color, bottom, alpha=255):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    poly = list(pts) + [(pts[-1][0], bottom), (pts[0][0], bottom)]
    d.polygon(poly, fill=color + (alpha,))
    canvas.alpha_composite(layer)


def grain(canvas, amount=3):
    w, h = canvas.size
    noise = Image.effect_noise((w, h), 26).convert("L")
    n = noise.point(lambda v: max(0, min(255, 128 + int((v - 128) * amount / 12))))
    layer = Image.merge("RGBA", (n, n, n, Image.new("L", (w, h), 16)))
    canvas.alpha_composite(layer)


# ---------------- 池面元素 ----------------
def ripple(canvas, cx, cy, n=7, r0=None, r1=None, color=(255, 255, 255),
           alpha=64, squash=0.58):
    """同心涟漪，压扁成椭圆模拟俯视透视"""
    r0 = r0 if r0 is not None else W * 0.06
    r1 = r1 if r1 is not None else W * 0.30
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(n):
        t = i / max(1, n - 1)
        r = r0 + (r1 - r0) * t
        a = int(alpha * (1 - t) ** 1.3)
        if a <= 2:
            continue
        d.ellipse([cx - r, cy - r * squash, cx + r, cy + r * squash],
                  outline=color + (a,), width=max(2, int((2.2 + 2.0 * t) * SS)))
    canvas.alpha_composite(layer)


def lily_pad(canvas, cx, cy, r, rgb, alpha=255, notch=22, rot=0, veins=True):
    """荷叶：带 V 形缺口的圆盘 + 放射叶脉 + 叶心"""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bbox = [cx - r, cy - r * 0.88, cx + r, cy + r * 0.88]
    a0 = rot + notch / 2
    a1 = rot + 360 - notch / 2
    d.pieslice(bbox, a0, a1, fill=rgb + (alpha,))
    if veins:
        vc = mix(rgb, (200, 244, 216), 0.55) + (int(alpha * 0.30),)
        for i in range(9):
            ang = math.radians(a0 + (a1 - a0) * i / 8)
            d.line([(cx, cy), (cx + math.cos(ang) * r * 0.90,
                               cy + math.sin(ang) * r * 0.79)],
                   fill=vc, width=max(1, int(1.8 * SS)))
    d.ellipse([cx - r * 0.085, cy - r * 0.075, cx + r * 0.085, cy + r * 0.075],
              fill=mix(rgb, (24, 76, 60), 0.45) + (alpha,))
    canvas.alpha_composite(layer)


def petal(canvas, cx, cy, ang_deg, length, width, fill):
    """单瓣：旋转椭圆，一端落在花心"""
    a = math.radians(ang_deg)
    px = cx + math.cos(a) * length * 0.5
    py = cy + math.sin(a) * length * 0.5
    lw, lh = int(length) + 8, int(width) + 8
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([3, 3, lw - 4, lh - 4], fill=fill)
    layer = layer.rotate(-ang_deg, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(layer, (int(px - layer.width / 2), int(py - layer.height / 2)))


def lotus(canvas, cx, cy, r, alpha=255, tone=(250, 238, 246)):
    """荷花：八瓣外层 + 六瓣内层 + 花蕊"""
    for i in range(8):
        petal(canvas, cx, cy, i * 45 + 22.5, r * 1.62, r * 0.78, tone + (int(alpha * 0.92),))
    for i in range(6):
        petal(canvas, cx, cy, i * 60 - 90, r * 1.10, r * 0.64,
              (247, 205, 224, int(alpha * 0.95)))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r * 0.30, cy - r * 0.26, cx + r * 0.30, cy + r * 0.26],
              fill=(252, 222, 132, int(alpha * 0.95)))
    d.ellipse([cx - r * 0.18, cy - r * 0.15, cx + r * 0.18, cy + r * 0.15],
              fill=(255, 240, 186, int(alpha * 0.9)))
    canvas.alpha_composite(layer)


def bud(canvas, cx, cy, r, alpha=255):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r * 0.42, cy - r, cx + r * 0.42, cy + r * 0.55],
              fill=(250, 228, 238, alpha))
    d.ellipse([cx - r * 0.30, cy - r * 0.86, cx + r * 0.30, cy + r * 0.10],
              fill=(244, 194, 214, alpha))
    canvas.alpha_composite(layer)


def bez(p0, p1, p2, n=22):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out


def boat(canvas, cx, cy, w, h, alpha=255):
    """小木船：两端上翘的尖头 + 浅碗形船身 + 两条横板"""
    hw, hh = w / 2.0, h / 2.0

    def P(ux, uy):
        return (cx + ux * hw, cy + uy * hh)

    # 轮廓：左尖 -> 船底 -> 右尖 -> 船口拱回左尖
    ship = (bez(P(-1.00, -0.06), P(-0.96, 0.34), P(-0.42, 0.54), 20)
            + bez(P(-0.42, 0.54), P(0, 0.62), P(0.42, 0.54), 18)[1:]
            + bez(P(0.42, 0.54), P(0.96, 0.34), P(1.00, -0.06), 20)[1:]
            + bez(P(1.00, -0.06), P(0.58, -0.56), P(0, -0.62), 20)[1:]
            + bez(P(0, -0.62), P(-0.58, -0.56), P(-1.00, -0.06), 20)[1:])

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 水面投影
    d.ellipse([cx - hw * 0.90, cy + hh * 0.22, cx + hw * 0.90, cy + hh * 0.86],
              fill=(56, 128, 120, int(alpha * 0.26)))

    d.polygon(ship, fill=(248, 242, 231, alpha))
    d.line(ship, fill=(188, 208, 202, alpha), width=max(2, int(3.2 * SS)), joint="curve")

    # 船口内侧：比船身暗一档
    inner = (bez(P(-0.86, -0.02), P(-0.50, -0.42), P(0, -0.46), 18)
             + bez(P(0, -0.46), P(0.50, -0.42), P(0.86, -0.02), 18)[1:]
             + bez(P(0.86, -0.02), P(0.44, 0.28), P(0, 0.30), 16)[1:]
             + bez(P(0, 0.30), P(-0.44, 0.28), P(-0.86, -0.02), 16)[1:])
    d.polygon(inner, fill=(226, 213, 191, alpha))

    # 两条横板（略微跟着船身弧）
    for uy in (-0.24, 0.04):
        pts = [(P(-0.56, uy)[0], P(-0.56, uy)[1]),
               (P(0, uy + 0.05)[0], P(0, uy + 0.05)[1]),
               (P(0.56, uy)[0], P(0.56, uy)[1])]
        d.line(pts, fill=(222, 208, 184, alpha), width=max(3, int(hh * 0.22)), joint="curve")
        d.line([(pts[0][0], pts[0][1] - hh * 0.085), (pts[1][0], pts[1][1] - hh * 0.085),
                (pts[2][0], pts[2][1] - hh * 0.085)],
               fill=(253, 249, 240, int(alpha * 0.85)), width=max(1, int(2.0 * SS)), joint="curve")

    # 船口上缘亮边
    top = (bez(P(-1.00, -0.06), P(-0.58, -0.56), P(0, -0.62), 22)
           + bez(P(0, -0.62), P(0.58, -0.56), P(1.00, -0.06), 22)[1:])
    d.line(top, fill=(255, 253, 246, int(alpha * 0.95)),
           width=max(2, int(3.6 * SS)), joint="curve")

    canvas.alpha_composite(layer)


def sparkle(canvas, n, box, seed=7, color=(255, 255, 255), alpha=120):
    """水面碎光"""
    rnd = random.Random(seed)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        r = rnd.uniform(W * 0.0012, W * 0.0042)
        a = int(alpha * rnd.uniform(0.35, 1.0))
        d.ellipse([x - r, y - r, x + r, y + r], fill=color + (a,))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(SS * 0.8)))


def leaf(canvas, cx, cy, ang, L, Wd, rgb, alpha=200):
    """漂浮落叶"""
    a = math.radians(ang)
    px = cx + math.cos(a) * L * 0.5
    py = cy + math.sin(a) * L * 0.5
    lw, lh = int(L) + 8, int(Wd) + 8
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([3, 3, lw - 4, lh - 4], fill=rgb + (alpha,))
    layer = layer.rotate(-ang, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(layer, (int(px - layer.width / 2), int(py - layer.height / 2)))


def soft_clouds(canvas):
    cloud = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cloud)
    for (cx, cy, rw, rh, al) in [(0.18, 0.070, 0.20, 0.030, 30),
                                 (0.52, 0.042, 0.26, 0.026, 24),
                                 (0.84, 0.085, 0.18, 0.024, 22)]:
        d.ellipse([W * (cx - rw), H * (cy - rh), W * (cx + rw), H * (cy + rh)],
                  fill=(255, 252, 250, al))
    canvas.alpha_composite(cloud.filter(ImageFilter.GaussianBlur(SS * 9)))


# ---------------- 主界面 ----------------
def build_main():
    canvas = vgrad(W, H, [
        (0.00, (246, 229, 244)),
        (0.07, (248, 237, 245)),
        (0.17, (238, 232, 238)),
        (0.27, (212, 231, 226)),
        (0.35, (182, 220, 212)),
        (0.44, (152, 206, 197)),
        (0.58, (124, 190, 182)),
        (0.72, (102, 174, 168)),
        (0.86, (84, 156, 152)),
        (1.00, (66, 136, 134)),
    ]).convert("RGBA")

    glow(canvas, W * 0.30, H * 0.10, H * 0.55, (255, 248, 242), peak=42)

    # 远岸：两层很淡的青色剪影
    far = profile([
        (0.00, 0.348), (0.06, 0.318), (0.13, 0.342), (0.20, 0.306),
        (0.28, 0.336), (0.36, 0.312), (0.44, 0.344), (0.52, 0.310),
        (0.60, 0.338), (0.68, 0.314), (0.76, 0.342), (0.84, 0.308),
        (0.92, 0.336), (1.00, 0.344)], sigma=5.5)
    fill_down(canvas, far, (176, 198, 208), H * 1.02, alpha=112)

    near = profile([
        (0.00, 0.384), (0.09, 0.360), (0.18, 0.378), (0.27, 0.352),
        (0.36, 0.376), (0.45, 0.356), (0.54, 0.380), (0.63, 0.354),
        (0.72, 0.376), (0.81, 0.358), (0.90, 0.380), (1.00, 0.372)], sigma=5.0)
    fill_down(canvas, near, (150, 184, 192), H * 1.02, alpha=124)

    # 水色把山脚化开，避免平切硬边
    # 水层：从山脚一路铺到画面底部，0.30~0.52 之间由透明渐到全不透明。
    # 关键是它不会中途结束，所以不会出现横线；山也就自然沉进水里。
    wtop, wbot = 0.300, 1.0
    water_h = int(H * (wbot - wtop))
    water = vgrad(W, water_h, [
        (0.00, (188, 222, 214)),
        (0.20, (156, 208, 199)),
        (0.42, (124, 194, 184)),
        (0.62, (102, 176, 168)),
        (0.80, (84, 158, 153)),
        (1.00, (64, 140, 136)),
    ]).convert("RGBA")
    ramp = Image.linear_gradient("L").resize((W, water_h), Image.BILINEAR)
    # 0~46% 从 0 渐到 255，之后保持不透明
    water.putalpha(ramp.point(lambda v: 255 if v >= 117 else int(v * 255 / 117)))
    canvas.alpha_composite(water, (0, int(H * wtop)))

    # 池面涟漪（以小船为中心）+ 碎光
    bx, by = W * 0.715, H * 0.775
    ripple(canvas, bx, by, n=8, r0=W * 0.075, r1=W * 0.40,
           color=(255, 255, 255), alpha=84, squash=0.56)
    sparkle(canvas, 90, (W * 0.40, H * 0.50, W * 0.98, H * 0.92), seed=11, alpha=96)

    # 荷叶：左侧一组
    lily_pad(canvas, W * 0.020, H * 0.700, W * 0.085, (66, 148, 118), 236, notch=26, rot=150)
    lily_pad(canvas, W * 0.105, H * 0.800, W * 0.115, (58, 138, 108), 244, notch=20, rot=40)
    lily_pad(canvas, W * 0.045, H * 0.945, W * 0.150, (48, 124, 98), 250, notch=24, rot=200)
    lily_pad(canvas, W * 0.205, H * 0.905, W * 0.095, (72, 158, 124), 244, notch=18, rot=95)
    lily_pad(canvas, W * 0.255, H * 1.010, W * 0.120, (44, 116, 92), 250, notch=28, rot=310)

    # 荷叶：右侧一组
    lily_pad(canvas, W * 0.935, H * 0.575, W * 0.072, (78, 164, 130), 232, notch=20, rot=70)
    lily_pad(canvas, W * 0.995, H * 0.735, W * 0.098, (60, 142, 112), 244, notch=24, rot=250)
    lily_pad(canvas, W * 0.870, H * 0.930, W * 0.108, (50, 128, 100), 248, notch=18, rot=120)
    lily_pad(canvas, W * 0.960, H * 1.000, W * 0.135, (42, 112, 90), 250, notch=30, rot=35)

    # 荷花与花苞
    bud(canvas, W * 0.082, H * 0.742, W * 0.020, 240)
    lotus(canvas, W * 0.168, H * 0.846, W * 0.048, 250)
    lotus(canvas, W * 0.905, H * 0.888, W * 0.040, 246)
    bud(canvas, W * 0.955, H * 0.640, W * 0.017, 230)

    # 小船
    boat(canvas, bx, by, W * 0.260, H * 0.158)

    # 漂浮落叶
    for (lx, ly, ang, L, col, al) in [
        (0.330, 0.700, 24, 0.020, (232, 214, 130), 190),
        (0.470, 0.900, -40, 0.017, (222, 206, 124), 175),
        (0.640, 0.610, 12, 0.015, (236, 220, 140), 170),
        (0.800, 0.700, -18, 0.018, (228, 210, 128), 165),
        (0.585, 0.955, 52, 0.019, (218, 200, 118), 180),
    ]:
        leaf(canvas, W * lx, H * ly, ang, W * L, W * L * 0.42, col, al)

    edge_shade(canvas, rgb=(30, 66, 66), top=0, bottom=int(H * 0.040),
               left=int(W * 0.010), right=int(W * 0.010), alpha=46)
    grain(canvas, 3)
    return canvas.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)


# ---------------- 游戏内 ----------------
def build_play():
    canvas = vgrad(W, H, [
        (0.00, (30, 60, 60)),
        (0.10, (34, 68, 66)),
        (0.26, (38, 76, 74)),
        (0.44, (32, 68, 68)),
        (0.62, (26, 58, 60)),
        (0.80, (18, 44, 48)),
        (1.00, (9, 24, 28)),
    ]).convert("RGBA")

    # 中央柔光，托住米色牌面
    glow(canvas, W * 0.50, H * 0.44, H * 0.90, (98, 172, 160), peak=74)
    # 顶部一点天光，避免上沿发死
    glow(canvas, W * 0.50, -H * 0.08, H * 0.60, (124, 190, 178), peak=46)

    # 极淡的水面反光，只做层次不抢戏
    ripple(canvas, W * 0.50, H * 0.505, n=4, r0=W * 0.22, r1=W * 0.72,
           color=(152, 216, 202), alpha=13, squash=0.32)

    # 底部荷叶丛（两端收在画面外，不留垂直断面）
    for (cx, cy, r, rot, al, col) in [
        (0.01, 0.955, 0.145, 165, 250, (13, 36, 38)),
        (0.15, 0.998, 0.118, 75, 250, (10, 30, 34)),
        (0.30, 1.022, 0.132, 105, 252, (8, 26, 30)),
        (0.44, 0.982, 0.098, 40, 248, (13, 36, 38)),
        (0.58, 1.018, 0.122, 350, 250, (9, 28, 32)),
        (0.72, 0.972, 0.102, 195, 248, (13, 36, 38)),
        (0.86, 1.012, 0.128, 85, 250, (8, 26, 30)),
        (0.99, 0.958, 0.138, 15, 250, (13, 36, 38)),
    ]:
        lily_pad(canvas, W * cx, H * cy, W * r, col, al, notch=26, rot=rot, veins=False)

    # 荷叶上缘一点冷光，否则只是一团黑
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for (cx, cy, r, rot) in [(0.01, 0.955, 0.145, 165), (0.30, 1.022, 0.132, 105),
                             (0.58, 1.018, 0.122, 350), (0.86, 1.012, 0.128, 85)]:
        bbox = [W * cx - W * r, H * cy - W * r * 0.88,
                W * cx + W * r, H * cy + W * r * 0.88]
        d.arc(bbox, rot + 14, rot + 172, fill=(104, 176, 158, 46),
              width=max(2, int(2.8 * SS)))
    canvas.alpha_composite(layer)

    # 水面微光
    sparkle(canvas, 34, (W * 0.16, H * 0.28, W * 0.84, H * 0.80), seed=23,
            color=(190, 236, 222), alpha=46)

    edge_shade(canvas, rgb=(4, 14, 18), top=0, bottom=int(H * 0.055),
               left=int(W * 0.018), right=int(W * 0.018), alpha=110)
    grain(canvas, 3)
    return canvas.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)


# ---------------- 入口 ----------------
def main():
    apply = "--apply" in sys.argv
    os.makedirs(os.path.join(ROOT, "Temp"), exist_ok=True)
    for fn, dest, preview in [(build_main, MAIN_SRC, "Temp/bg_new_main.png"),
                              (build_play, PLAY_SRC, "Temp/bg_new_play.png")]:
        img = fn()
        img.save(os.path.join(ROOT, preview))
        print("%-12s %s -> %s" % (os.path.basename(dest), img.size, preview))
        if apply:
            img.save(os.path.join(ROOT, dest))
            print("   已覆盖", dest)
    print("apply =", apply)


if __name__ == "__main__":
    main()
