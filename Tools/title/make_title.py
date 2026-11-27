# -*- coding: utf-8 -*-
"""
生成游戏主标题图（多行、纵向渐变、白描边、顶部高光、柔和投影）。

替换 Assets/Images/MainSence/Appname.png —— 这张是主界面 Main.unity 里
名为 Image 的节点（RectTransform 315x195，PreserveAspect 1），实际按原图
等比显示，所以画布尺寸必须和原图一致，只换像素。

为什么是两行：1358x840 画布一行放 7 个字，每字只有 182px，等比缩到 315 宽
的框里只剩 42 单位，比原来 4 字/行（约 305px）小近一半，手机上会糊。沿用
原图 4+2 的版式，字才够粗。

用法：
    python Tools/title/make_title.py              # 预览 -> Temp/title_preview/
    python Tools/title/make_title.py --apply      # 覆盖 Assets 原图
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONT = os.path.join(ROOT, "Assets/AdSDK/Font/DroidSansFallback.ttf")
S = 2  # 超采样倍数（1358x840 底图不宜用 4，内存吃紧）

# 白描边 / 深色内边 / 字身加粗，按字号取比例
# 参考图是清透的水绿字：白边要细，内边要淡，太粗会像卡通贴纸一样发闷
WHITE_R, RIM_R, BODY_R = 0.082, 0.028, 0.018

JOBS = [
    dict(
        path="Assets/Images/MainSence/Appname.png",
        lines=[
            ("闲舟静泛", 0.80, 0.500),   # 文案, 目标宽度占比, 该行最大高度占比
            ("清波", 0.455, 0.460),
        ],
        fill=((228, 252, 242), (48, 158, 138)),   # 极浅薄荷 -> 青绿
        track=0.060,
        shadow=(20, 78, 70, 78),
        glow=(176, 240, 222),                     # 外发光色
    ),
]


def darken(c, k=0.72):
    return tuple(int(v * k) for v in c[:3])


def char_w(font, ch):
    bb = font.getbbox(ch)
    return bb[2] - bb[0]


def total_w(font, chars, tracking):
    return sum(char_w(font, c) for c in chars) + tracking * (len(chars) - 1)


def draw_line(layer, chars, font, tracking, x0, y0, fill, stroke=None, stroke_w=0):
    d = ImageDraw.Draw(layer)
    x = x0
    for ch in chars:
        d.text((x, y0), ch, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)
        x += char_w(font, ch) + tracking


def fit(chars, w, h, max_w, max_h, track_ratio):
    """在给定画布内找最大的可用字号（宽度、高度、字距三重约束）"""
    size = int(min(max_h, max_w))
    while size > 10:
        font = ImageFont.truetype(FONT, size)
        tracking = int(size * track_ratio)
        border = size * WHITE_R
        ok_w = total_w(font, chars, tracking) + 2 * border <= max_w
        ok_h = size * 0.90 + 2 * border <= max_h
        ok_gap = len(chars) < 2 or tracking >= 1.6 * border
        if ok_w and ok_h and ok_gap:
            return font, tracking
        if not ok_gap:
            track_ratio += 0.04
        else:
            size -= 2
    raise RuntimeError("字号放不下：" + "".join(chars))


def build(job):
    src = Image.open(os.path.join(ROOT, job["path"])).convert("RGBA")
    W, H = src.size
    w, h = W * S, H * S

    metrics = []
    for text, wr, hr in job["lines"]:
        chars = list(text)
        font, tracking = fit(chars, w, h, w * wr, h * hr, job["track"])
        size = font.size
        ref = font.getbbox("国")
        glyph_h = ref[3] - ref[1]
        tw = total_w(font, chars, tracking)
        metrics.append(dict(chars=chars, font=font, size=size, tracking=tracking,
                            glyph_h=glyph_h, tw=tw, ref_top=ref[1],
                            first_left=font.getbbox(chars[0])[0]))

    # 垂直堆叠：行距必须容下两行的白描边，否则描边会糊成一片
    border1 = metrics[0]["size"] * WHITE_R
    border2 = metrics[-1]["size"] * WHITE_R
    gap = int((border1 + border2) * 1.35)
    total_h = sum(m["glyph_h"] for m in metrics) + gap * (len(metrics) - 1)
    if total_h > h * 0.94:
        raise RuntimeError("两行加起来放不下：%d > %d，调小 width_ratio" % (total_h, h * 0.94))
    top = (h - total_h) // 2

    cursor = top
    for m in metrics:
        m["x0"] = (w - m["tw"]) // 2 - m["first_left"]
        m["y0"] = cursor - m["ref_top"]
        m["line_top"] = cursor
        cursor += m["glyph_h"] + gap

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # 1) 投影
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for m in metrics:
        draw_line(shadow, m["chars"], m["font"], m["tracking"],
                  m["x0"], m["y0"] + int(m["size"] * 0.055), job["shadow"])
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(S * 1.3)))

    # 2) 外发光：柔和的青绿晕，让字从水面上"浮"起来
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gcol = job["glow"] + (255,)
    for m in metrics:
        draw_line(glow, m["chars"], m["font"], m["tracking"], m["x0"], m["y0"],
                  gcol, gcol, max(2, int(m["size"] * 0.07)))
    glow = glow.filter(ImageFilter.GaussianBlur(S * 2.2))
    glow.putalpha(glow.split()[3].point(lambda v: int(v * 0.22)))
    canvas.alpha_composite(glow)

    # 3) 白描边
    outline = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for m in metrics:
        draw_line(outline, m["chars"], m["font"], m["tracking"], m["x0"], m["y0"],
                  (255, 255, 255, 255), (255, 255, 255, 255),
                  max(2, int(m["size"] * WHITE_R)))
    canvas.alpha_composite(outline)

    # 4) 深色内边（让浅色字在水面上有边界）
    rim_color = darken(job["fill"][1], 0.80) + (255,)
    rim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for m in metrics:
        draw_line(rim, m["chars"], m["font"], m["tracking"], m["x0"], m["y0"],
                  rim_color, rim_color, max(1, int(m["size"] * RIM_R)))
    canvas.alpha_composite(rim)

    # 5) 字身渐变（两行共用同一条纵向渐变，视觉统一）
    mask = Image.new("L", (w, h), 0)
    for m in metrics:
        draw_line(mask, m["chars"], m["font"], m["tracking"], m["x0"], m["y0"],
                  255, 255, max(1, int(m["size"] * BODY_R)))
    top_c, bot_c = job["fill"]
    body = Image.new("RGBA", (w, h))
    px = body.load()
    for y in range(h):
        t = (y / max(1, h - 1)) ** 0.80
        c = tuple(int(top_c[i] + (bot_c[i] - top_c[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c + (255,)
    body.putalpha(mask)
    canvas.alpha_composite(body)

    # 5) 每行顶部高光
    for m in metrics:
        band = max(2, int(m["glyph_h"] * 0.38))
        agrad = ImageOps.invert(Image.linear_gradient("L")).resize((w, band), Image.BILINEAR)
        hi = Image.new("L", (w, h), 0)
        hi.paste(agrad.point(lambda v: int(v * 0.46)), (0, int(m["line_top"])))
        merged = Image.composite(hi, Image.new("L", (w, h), 0), mask)
        glow = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        glow.putalpha(merged)
        canvas.alpha_composite(glow)

    return canvas.resize((W, H), Image.LANCZOS)


def edge_alpha(img):
    a = img.split()[3]
    w, h = a.size
    px = a.load()
    m = 0
    for x in range(w):
        m = max(m, px[x, 0], px[x, h - 1])
    for y in range(h):
        m = max(m, px[0, y], px[w - 1, y])
    return m


def main():
    apply = "--apply" in sys.argv
    outdir = os.path.join(ROOT, "Temp/title_preview")
    os.makedirs(outdir, exist_ok=True)
    for job in JOBS:
        img = build(job)
        name = os.path.basename(job["path"])
        img.save(os.path.join(outdir, name))
        print("%-16s %-14s 边缘alpha=%d" % (name, str(img.size), edge_alpha(img)))
        if apply:
            img.save(os.path.join(ROOT, job["path"]))
            print("  -> 已覆盖", job["path"])
    print("apply =", apply)


if __name__ == "__main__":
    main()
