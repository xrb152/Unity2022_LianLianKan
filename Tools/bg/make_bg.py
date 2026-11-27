# -*- coding: utf-8 -*-
"""
「寻秘奔赴·山海」主题背景（扁平国风插画）
  Assets/Images/MainSence/back1.png  — 主界面，UI Image 拉伸铺满
  Assets/Images/playUI/playBg.png    — 游戏内/帮助页，SpriteRenderer cover 裁切
用法：
  python Tools/bg/make_bg.py            # 预览 -> Temp/bg_new_*.png
  python Tools/bg/make_bg.py --apply    # 覆盖原图（尺寸恒为 1920x1080）
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_W, OUT_H = 1920, 1080
SS = 2
W, H = OUT_W * SS, OUT_H * SS


# ---------------- 工具 ----------------
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


def glow(canvas, cx, cy, radius, rgb, peak=180, falloff=1.8, steps=44):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(steps, 0, -1):
        t = i / steps
        r = radius * t
        a = int(peak * ((1.0 - t) ** falloff))
        if a > 0:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb + (a,))
    canvas.alpha_composite(layer)


def edge_shade(canvas, rgb=(10, 26, 34), top=0, bottom=0, left=0, right=0, power=1.8):
    w, h = canvas.size
    layer = Image.new("RGBA", canvas.size, rgb + (0,))
    px = layer.load()

    def ramp(n):
        return [int(255 * ((1.0 - i / max(1, n - 1)) ** power)) for i in range(n)]

    if top:
        for y, a in enumerate(ramp(top)):
            for x in range(w):
                px[x, y] = rgb + (a,)
    if bottom:
        for y, a in enumerate(reversed(ramp(bottom))):
            for x in range(w):
                px[x, h - bottom + y] = rgb + (a,)
    if left:
        for x, a in enumerate(ramp(left)):
            for y in range(h):
                px[x, y] = rgb + (a,)
    if right:
        for x, a in enumerate(reversed(ramp(right))):
            for y in range(h):
                px[w - right + x, y] = rgb + (a,)
    canvas.alpha_composite(layer)


def smooth1d(vals, sigma):
    if sigma <= 0:
        return list(vals)
    r = max(1, int(sigma * 2.5))
    kern = [math.exp(-(i * i) / (2.0 * sigma * sigma)) for i in range(-r, r + 1)]
    s = sum(kern)
    kern = [k / s for k in kern]
    n = len(vals)
    out = []
    for i in range(n):
        acc = 0.0
        for j, k in enumerate(kern):
            idx = i + j - r
            idx = 0 if idx < 0 else (n - 1 if idx >= n else idx)
            acc += vals[idx] * k
        out.append(acc)
    return out


def profile(ctrl, sigma=6.0, samples=1100):
    """ctrl=[(x_norm, y_norm)] 升序；线性插值 + 高斯平滑，只返回控制点跨度内的点"""
    xs = [c[0] * W for c in ctrl]
    ys = [c[1] for c in ctrl]
    x_start, x_end = xs[0], xs[-1]
    raw, pxs = [], []
    for i in range(samples + 1):
        x = x_start + (x_end - x_start) * i / samples
        k = 0
        while k < len(xs) - 2 and x > xs[k + 1]:
            k += 1
        seg = (xs[k + 1] - xs[k]) or 1.0
        t = (x - xs[k]) / seg
        raw.append(ys[k] + (ys[k + 1] - ys[k]) * t)
        pxs.append(x)
    sm = smooth1d(raw, sigma)
    return [(pxs[i], sm[i] * H) for i in range(len(pxs))]


def fill_down(canvas, pts, color, bottom, alpha=255, blur=0.0):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon(pts + [(pts[-1][0], bottom), (pts[0][0], bottom)], fill=color + (alpha,))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(layer)


def wave_arcs(canvas, y, amp, span_list, color, alpha, thick, seed=0):
    """分段水波：按 span_list 给的分段各自画一段正弦弧"""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    for (xa, xb) in span_list:
        x0, x1 = xa * W, xb * W
        ph = rnd.uniform(0, math.tau)
        wl = W * rnd.uniform(0.05, 0.11)
        pts = []
        step = max(4, int((x1 - x0) / 60))
        for x in range(int(x0), int(x1), step):
            pts.append((x, y + math.sin((x - x0) / wl * math.tau + ph) * amp))
        if len(pts) > 1:
            d.line(pts, fill=color + (alpha,), width=int(thick), joint="curve")
    canvas.alpha_composite(layer)


def cloud(canvas, cx, cy, w, h, rgb=(255, 255, 255), alpha=225):
    """自然积云：4 个不对称圆团 + 平底"""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = rgb + (alpha,)
    d.ellipse([cx - w * 0.50, cy - h * 0.55, cx + w * 0.50, cy + h * 0.62], fill=col)
    d.ellipse([cx - w * 0.40, cy - h * 1.15, cx - w * 0.02, cy + h * 0.30], fill=col)
    d.ellipse([cx - w * 0.14, cy - h * 1.62, cx + w * 0.30, cy + h * 0.10], fill=col)
    d.ellipse([cx + w * 0.16, cy - h * 0.95, cx + w * 0.46, cy + h * 0.26], fill=col)
    d.ellipse([cx - w * 0.46, cy + h * 0.02, cx + w * 0.46, cy + h * 0.62], fill=col)
    canvas.alpha_composite(layer)


def scroll_frame(canvas, rgb=(240, 202, 136), alpha=40, inset=None, width=3, radius=None):
    w, h = canvas.size
    inset = inset or int(min(w, h) * 0.030)
    radius = radius or int(min(w, h) * 0.030)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([inset, inset, w - inset, h - inset], radius=radius,
                        outline=rgb + (alpha,), width=int(width * SS / 2))
    canvas.alpha_composite(layer)


def rock_band(top_pts, shore_pts, drop=0.0, seg=12):
    """礁石闭合轮廓：顶部为山石轮廓，底部沿沙面曲线回收"""
    top = list(top_pts)
    xa, xb = top[0][0], top[-1][0]
    n = len(shore_pts)
    bot = []
    for i in range(seg + 1):
        x = xb - (xb - xa) * i / seg
        k = min(n - 1, max(0, int(round(x / W * (n - 1)))))
        bot.append((x, shore_pts[k][1] + H * 0.002 + drop))
    return top + bot


def cloud_curl(canvas, cx, cy, r, alpha=52, lw=2.4, arcs=(0.58, 0.78, 1.00),
               a0=196, a1=336, rgb=(242, 206, 148)):
    """国风云气：同心弧线（角落装饰）"""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for mult in arcs:
        rr = r * mult
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1,
              fill=rgb + (alpha,), width=max(1, int(lw * SS)))
    canvas.alpha_composite(layer)


def grain(canvas, amount=4):
    noise = Image.effect_noise(canvas.size, 16).convert("L")
    layer = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    layer.putalpha(noise.point(lambda v: int(abs(v - 128) / 128.0 * amount)))
    canvas.alpha_composite(layer)


# ---------------- 主界面：晨光海湾 ----------------
def build_main():
    canvas = vgrad(W, H, [
        (0.00, (74, 146, 170)),
        (0.12, (98, 170, 188)),
        (0.28, (140, 198, 204)),
        (0.42, (188, 218, 206)),
        (0.50, (232, 216, 180)),   # 地平线暖雾
        (0.56, (206, 216, 192)),
        (0.62, (118, 182, 184)),
        (0.72, (86, 160, 168)),
        (0.85, (52, 118, 134)),
        (1.00, (30, 84, 104)),
    ]).convert("RGBA")

    # ---- 太阳 ----
    sx, sy = W * 0.63, H * 0.285
    r = H * 0.046
    glow(canvas, sx, sy, H * 0.34, (255, 224, 168), peak=56, falloff=2.3)
    d = ImageDraw.Draw(canvas)
    for mult, a, lw in [(2.15, 22, 2.0), (1.62, 34, 2.2), (1.30, 46, 2.4)]:
        rr = r * mult
        d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=(255, 238, 194, a),
                  width=int(lw * SS))
    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 214, 138, 255))
    d.ellipse([sx - r * 0.74, sy - r * 0.74, sx + r * 0.74, sy + r * 0.74], fill=(255, 234, 182, 255))

    # ---- 云 ----
    cloud(canvas, W * 0.175, H * 0.150, W * 0.235, H * 0.026, alpha=228)
    cloud(canvas, W * 0.455, H * 0.098, W * 0.185, H * 0.020, alpha=190)
    cloud(canvas, W * 0.845, H * 0.180, W * 0.215, H * 0.022, alpha=210)
    cloud(canvas, W * 0.315, H * 0.372, W * 0.270, H * 0.013, alpha=120)
    cloud(canvas, W * 0.720, H * 0.418, W * 0.230, H * 0.011, alpha=104)

    # ---- 远处飞鸟 ----
    lb = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    db = ImageDraw.Draw(lb)
    for (bx, by, bs, al) in [(0.400, 0.238, 0.0115, 128), (0.442, 0.198, 0.0085, 104),
                             (0.474, 0.252, 0.0092, 92), (0.506, 0.214, 0.0072, 78)]:
        x, y, sp = bx * W, by * H, bs * H
        db.line([(x - sp, y + sp * 0.48), (x - sp * 0.44, y - sp * 0.28), (x, y + sp * 0.12),
                 (x + sp * 0.44, y - sp * 0.28), (x + sp, y + sp * 0.48)],
                fill=(28, 64, 76, al), width=max(2, int(2.0 * SS)), joint="curve")
    canvas.alpha_composite(lb)

    # ---- 远山（雾青）----
    far = profile([
        (0.00, 0.566), (0.055, 0.522), (0.100, 0.484), (0.155, 0.524),
        (0.210, 0.552), (0.265, 0.508), (0.320, 0.470), (0.378, 0.516),
        (0.435, 0.556), (0.492, 0.512), (0.545, 0.476), (0.600, 0.522),
        (0.655, 0.558), (0.712, 0.514), (0.768, 0.478), (0.822, 0.524),
        (0.878, 0.556), (0.935, 0.516), (1.00, 0.548)], sigma=4.2)
    fill_down(canvas, far, (170, 202, 194), H * 1.02, alpha=240)

    # ---- 中山（青绿，海岬有开有合）----
    mid = profile([
        (0.00, 0.624), (0.03, 0.590), (0.06, 0.548), (0.09, 0.502),
        (0.115, 0.462), (0.140, 0.508), (0.170, 0.556), (0.205, 0.596),
        (0.240, 0.622), (0.285, 0.638), (0.330, 0.626), (0.370, 0.600),
        (0.405, 0.564), (0.440, 0.522), (0.470, 0.478), (0.500, 0.520),
        (0.535, 0.566), (0.570, 0.604), (0.610, 0.628), (0.660, 0.640),
        (0.705, 0.622), (0.745, 0.592), (0.785, 0.556), (0.820, 0.516),
        (0.850, 0.474), (0.880, 0.518), (0.912, 0.566), (0.945, 0.606),
        (0.975, 0.628), (1.00, 0.636)], sigma=3.2)
    fill_down(canvas, mid, (104, 156, 152), H * 1.02, alpha=248)

    # ---- 近山（深青，只占两侧 → 中间留出海口）----
    near_l = profile([
        (0.000, 0.648), (0.022, 0.612), (0.045, 0.584), (0.068, 0.560),
        (0.092, 0.546), (0.118, 0.568), (0.146, 0.596), (0.178, 0.624),
        (0.212, 0.658), (0.250, 0.698), (0.290, 0.742), (0.330, 0.794),
        (0.368, 0.852), (0.398, 0.912), (0.414, 1.000)], sigma=2.6)
    fill_down(canvas, near_l, (48, 104, 112), H * 1.02)
    near_r = profile([
        (0.586, 1.000), (0.602, 0.912), (0.632, 0.852), (0.670, 0.794),
        (0.710, 0.742), (0.750, 0.698), (0.788, 0.658), (0.822, 0.624),
        (0.854, 0.596), (0.882, 0.568), (0.908, 0.546), (0.932, 0.560),
        (0.955, 0.584), (0.978, 0.612), (1.000, 0.648)], sigma=2.6)
    fill_down(canvas, near_r, (42, 96, 106), H * 1.02)

    # ---- 水层：山脚渐隐入水 ----
    wx0, wx1 = 0, W
    water_h = int(H * 0.44)
    water = vgrad(W, water_h, [
        (0.00, (158, 210, 202)),
        (0.16, (122, 190, 190)),
        (0.42, (86, 162, 172)),
        (0.70, (58, 130, 148)),
        (1.00, (34, 96, 118)),
    ]).convert("RGBA")
    ramp = Image.linear_gradient("L").resize((W, water_h), Image.BILINEAR)
    water.putalpha(ramp.point(lambda v: int(214 * (v / 255.0) ** 1.22)))
    canvas.alpha_composite(water, (wx0, int(H * 0.575)))

    # ---- 太阳倒影 ----
    refl = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(refl)
    top_y, bot_y = H * 0.655, H * 0.862
    for i in range(26):  # 柔光带
        t = i / 25.0
        yy = top_y + (bot_y - top_y) * t
        half = W * (0.020 + 0.098 * t)
        a = int(44 * (1.0 - t) ** 1.35) + 3
        dr.line([(sx - half, yy), (sx + half, yy)],
                fill=(255, 230, 180, a), width=int((5 + 8 * t) * SS))
    refl = refl.filter(ImageFilter.GaussianBlur(H * 0.011))
    canvas.alpha_composite(refl)

    spark = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(spark)
    rnd = random.Random(99)
    for _ in range(9):  # 水面粼光（宽扁光斑）
        t = rnd.random() ** 1.1
        yy = top_y + (bot_y - top_y) * t
        half = W * (0.020 + 0.098 * t)
        cx = sx + rnd.uniform(-half * 0.40, half * 0.40)
        ln = W * rnd.uniform(0.045, 0.115) * (0.45 + t)
        hh = H * (0.004 + 0.006 * t)
        a = int(70 * (1.0 - t) ** 1.1) + 10
        ds.ellipse([cx - ln, yy - hh, cx + ln, yy + hh], fill=(255, 240, 200, a))
    spark = spark.filter(ImageFilter.GaussianBlur(H * 0.004))
    canvas.alpha_composite(spark)

    lite = (214, 240, 236)
    wave_arcs(canvas, H * 0.678, H * 0.0045, [(0.02, 0.30), (0.36, 0.52), (0.56, 0.95)],
              lite, 108, 2.4 * SS, 11)
    wave_arcs(canvas, H * 0.715, H * 0.0055, [(0.06, 0.26), (0.34, 0.60), (0.66, 0.98)],
              lite, 92, 2.6 * SS, 12)
    wave_arcs(canvas, H * 0.756, H * 0.0060, [(0.02, 0.34), (0.42, 0.72), (0.78, 0.99)],
              lite, 78, 2.8 * SS, 13)
    wave_arcs(canvas, H * 0.800, H * 0.0050, [(0.10, 0.40), (0.48, 0.88)], lite, 62, 3.0 * SS, 14)
    wave_arcs(canvas, H * 0.845, H * 0.0045, [(0.04, 0.30), (0.40, 0.70), (0.76, 0.96)],
              lite, 48, 3.2 * SS, 15)

    # ---- 沙洲 ----
    shore = profile([
        (0.00, 0.888), (0.10, 0.902), (0.22, 0.894), (0.35, 0.906),
        (0.48, 0.897), (0.60, 0.908), (0.72, 0.898), (0.85, 0.907),
        (1.00, 0.899)], sigma=9)
    fill_down(canvas, shore, (242, 217, 168), H * 1.02, alpha=255)
    shore2 = profile([
        (0.00, 0.940), (0.14, 0.951), (0.28, 0.942), (0.42, 0.955),
        (0.56, 0.944), (0.70, 0.956), (0.84, 0.945), (1.00, 0.953)], sigma=8)
    fill_down(canvas, shore2, (218, 183, 128), H * 1.02, alpha=255)

    # ---- 左右礁石（轮廓沿沙面闭合）----
    def rock_poly(pts):
        return [(x * W, y * H) for (x, y) in pts]

    rock_l = rock_poly([
        (0.004, 0.916), (0.016, 0.882), (0.034, 0.868), (0.050, 0.876),
        (0.062, 0.898), (0.076, 0.904), (0.090, 0.884), (0.106, 0.876),
        (0.122, 0.892), (0.134, 0.912), (0.142, 0.918), (0.148, 0.946),
        (0.104, 0.952), (0.058, 0.944), (0.014, 0.950)])
    rock_r = rock_poly([
        (0.858, 0.918), (0.866, 0.892), (0.878, 0.876), (0.894, 0.884),
        (0.908, 0.904), (0.922, 0.898), (0.936, 0.876), (0.952, 0.868),
        (0.968, 0.882), (0.984, 0.916), (0.990, 0.950), (0.946, 0.944),
        (0.900, 0.952), (0.872, 0.946)])
    for poly, col in ((rock_l, (32, 72, 86)), (rock_r, (28, 64, 78))):
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        dd = ImageDraw.Draw(layer)
        dd.polygon(poly, fill=col + (255,))
        canvas.alpha_composite(layer)

    # ---- 岸线浪花（只在岸线附近，不横贯）----
    foam = profile([
        (0.00, 0.886), (0.10, 0.900), (0.22, 0.892), (0.35, 0.904),
        (0.48, 0.895), (0.60, 0.906), (0.72, 0.896), (0.85, 0.905),
        (1.00, 0.897)], sigma=9)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    seg = [pt for pt in foam if 0.02 * W < pt[0] < 0.36 * W]
    seg2 = [pt for pt in foam if 0.48 * W < pt[0] < 0.72 * W]
    seg3 = [pt for pt in foam if 0.82 * W < pt[0] < 0.98 * W]
    for sg in (seg, seg2, seg3):
        if len(sg) > 2:
            d.line(sg, fill=(250, 252, 246, 130), width=int(3.0 * SS), joint="curve")
    layer = layer.filter(ImageFilter.GaussianBlur(2.4))
    canvas.alpha_composite(layer)

    for (cx, cy, a0, a1) in ((W * 0.052, H * 0.062, 8, 96), (W * 0.948, H * 0.062, 84, 172)):
        cloud_curl(canvas, cx, cy, H * 0.075, alpha=52, lw=2.4, a0=a0, a1=a1,
                   rgb=(250, 232, 186))

    scroll_frame(canvas)
    edge_shade(canvas, rgb=(26, 60, 74), top=34, bottom=64, left=26, right=26, power=2.0)
    grain(canvas, 4)
    return canvas.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)


# ---------------- 游戏内：幽谷（暗调托牌面）----------------
def build_play():
    canvas = vgrad(W, H, [
        (0.00, (18, 40, 54)),
        (0.10, (24, 54, 70)),
        (0.34, (36, 80, 94)),
        (0.55, (32, 74, 88)),
        (0.78, (22, 54, 68)),
        (1.00, (10, 28, 40)),
    ]).convert("RGBA")

    # 中央柔光：托住牌面，避免中间发闷
    glow(canvas, W * 0.50, H * 0.46, H * 0.82, (112, 170, 158), peak=44, falloff=2.2)

    # 主山：高低错落，有主峰，峰顶尖锐
    mtn = profile([
        (0.00, 0.334), (0.04, 0.302), (0.08, 0.324), (0.12, 0.288),
        (0.155, 0.248), (0.192, 0.212), (0.222, 0.262), (0.252, 0.302),
        (0.290, 0.320), (0.325, 0.284), (0.355, 0.236), (0.385, 0.198),
        (0.415, 0.258), (0.448, 0.308), (0.482, 0.322), (0.515, 0.286),
        (0.545, 0.246), (0.575, 0.222), (0.605, 0.268), (0.638, 0.308),
        (0.672, 0.320), (0.705, 0.280), (0.735, 0.230), (0.765, 0.188),
        (0.795, 0.250), (0.825, 0.302), (0.855, 0.322), (0.890, 0.290),
        (0.922, 0.320), (0.958, 0.338), (1.00, 0.346)], sigma=8.5)
    fill_down(canvas, mtn, (24, 58, 74), H * 1.02, alpha=246)

    # 云雾：山脚渐隐入雾
    mist_h = int(H * 0.32)
    mist = vgrad(W, mist_h, [
        (0.00, (42, 86, 100)),
        (0.42, (36, 78, 92)),
        (0.72, (30, 66, 80)),
        (1.00, (25, 58, 72)),
    ]).convert("RGBA")
    ramp = Image.linear_gradient("L").resize((W, mist_h), Image.BILINEAR)
    mist.putalpha(ramp.point(lambda v: int(208 * (v / 255.0) ** 0.92)))
    canvas.alpha_composite(mist, (0, int(H * 0.182)))

    # 雾后再补一点柔光，保证中央通透
    glow(canvas, W * 0.50, H * 0.52, H * 0.62, (120, 178, 166), peak=26, falloff=2.1)

    # 底部礁石（两端收在画面外，无垂直断面）
    bot = profile([
        (0.000, 1.040), (0.030, 0.966), (0.062, 0.938), (0.098, 0.958),
        (0.135, 0.930), (0.175, 0.956), (0.218, 0.930), (0.258, 0.958),
        (0.302, 0.934), (0.346, 0.960), (0.390, 0.936), (0.434, 0.962),
        (0.478, 0.938), (0.522, 0.960), (0.566, 0.936), (0.610, 0.962),
        (0.654, 0.938), (0.698, 0.960), (0.742, 0.934), (0.786, 0.958),
        (0.830, 0.930), (0.872, 0.956), (0.914, 0.930), (0.958, 0.956),
        (1.000, 1.040)], sigma=7.5, samples=800)
    fill_down(canvas, bot, (9, 26, 36), H * 1.045, alpha=252)

    bot2 = profile([
        (0.000, 1.040), (0.070, 0.998), (0.150, 0.978), (0.230, 0.998),
        (0.310, 0.978), (0.390, 1.000), (0.470, 0.978), (0.550, 1.000),
        (0.630, 0.978), (0.710, 1.000), (0.790, 0.978), (0.870, 1.000),
        (0.940, 0.982), (1.000, 1.040)], sigma=8.0, samples=800)
    fill_down(canvas, bot2, (6, 18, 26), H * 1.045, alpha=255)

    # 极淡波纹
    wave_arcs(canvas, H * 0.560, H * 0.0040, [(0.20, 0.44), (0.54, 0.78)], (176, 226, 224), 28, 2.0 * SS, 31)
    wave_arcs(canvas, H * 0.660, H * 0.0045, [(0.14, 0.40), (0.48, 0.74), (0.80, 0.94)], (176, 226, 224), 23, 2.2 * SS, 32)
    wave_arcs(canvas, H * 0.760, H * 0.0040, [(0.22, 0.50), (0.58, 0.86)], (176, 226, 224), 18, 2.2 * SS, 33)
    wave_arcs(canvas, H * 0.860, H * 0.0035, [(0.16, 0.44), (0.52, 0.82)], (176, 226, 224), 14, 2.2 * SS, 34)

    # 山脊 / 礁石金色边光
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.line([pt for pt in bot if pt[1] < H * 0.996], fill=(242, 202, 136, 46),
           width=int(3.0 * SS), joint="curve")
    d.line([pt for pt in mtn if pt[1] < H * 0.34 * H / H], fill=(240, 200, 136, 26),
           width=int(2.2 * SS), joint="curve")
    canvas.alpha_composite(layer)

    # 四角云气纹
    for (cx, cy, a0, a1) in ((W * 0.055, H * 0.070, 8, 96), (W * 0.945, H * 0.070, 84, 172),
                             (W * 0.055, H * 0.945, 264, 352), (W * 0.945, H * 0.945, 188, 276)):
        cloud_curl(canvas, cx, cy, H * 0.070, alpha=40, lw=2.2, a0=a0, a1=a1)

    scroll_frame(canvas, alpha=26)
    edge_shade(canvas, rgb=(5, 16, 24), top=50, bottom=78, left=42, right=42, power=1.9)
    grain(canvas, 4)
    return canvas.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)


def main():
    apply = "--apply" in sys.argv
    a = build_main()
    b = build_play()
    if apply:
        for img, rel in [(a, "Assets/Images/MainSence/back1.png"),
                         (b, "Assets/Images/playUI/playBg.png")]:
            p = os.path.join(ROOT, rel)
            img.save(p, optimize=True)
            print("写入", rel, img.size, "%.0f KB" % (os.path.getsize(p) / 1024))
    else:
        for img, name in [(a, "bg_new_main.png"), (b, "bg_new_play.png")]:
            p = os.path.join(ROOT, "Temp", name)
            img.save(p)
            print("预览", name, "%.0f KB" % (os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()
