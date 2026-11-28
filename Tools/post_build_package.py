# -*- coding: utf-8 -*-
"""
抖音小游戏导出后处理：清理调试符号 + 检查包体是否超限。
每次 Unity 重新导出到 tt-minigame 后运行一次：

    python Tools/post_build_package.py

抖音小游戏限制：
  主包 <= 4MB，单个分包 <= 20MB，整体(主包+所有分包) <= 20MB
"""
import os, sys, shutil, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG_ROOT = os.path.join(ROOT, "tt-minigame")
GAME_DIR = os.path.join(PKG_ROOT, "tt-minigame")
SYMBOL_BACKUP = os.path.join(PKG_ROOT, "symbols")

MAIN_LIMIT = 4 * 1024 * 1024
TOTAL_LIMIT = 20 * 1024 * 1024


def dir_size(path):
    total = 0
    for dp, _, fns in os.walk(path):
        for fn in fns:
            fp = os.path.join(dp, fn)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def mb(n):
    return n / 1048576.0


def main():
    if not os.path.isdir(GAME_DIR):
        print("!! 未找到上传目录:", GAME_DIR)
        return 1

    # 1) 移出 symbols
    os.makedirs(SYMBOL_BACKUP, exist_ok=True)
    moved = []
    for dp, _, fns in os.walk(GAME_DIR):
        for fn in fns:
            if "symbols" in fn.lower():
                src = os.path.join(dp, fn)
                dst = os.path.join(SYMBOL_BACKUP, fn)
                shutil.move(src, dst)
                moved.append((fn, os.path.getsize(dst)))
    if moved:
        for fn, sz in moved:
            print(f"已移出调试符号: {fn} ({mb(sz):.2f} MB)")
    else:
        print("未发现需移出的符号文件")

    # 2) 统计
    game_json = os.path.join(GAME_DIR, "game.json")
    try:
        cfg = json.load(open(game_json, encoding="utf-8"))
    except Exception:
        cfg = {}
    subs = [s.get("root", "").rstrip("/") for s in cfg.get("subpackages", [])]

    sub_sizes = {}
    for s in subs:
        p = os.path.join(GAME_DIR, s)
        if os.path.isdir(p):
            sub_sizes[s] = dir_size(p)

    total = dir_size(GAME_DIR)
    main_size = total - sum(sub_sizes.values())

    print("\n=== 包体报告 ===")
    print(f"  主包:   {mb(main_size):7.2f} MB   (限制 4.00)   {'OK' if main_size <= MAIN_LIMIT else '超限'}")
    for s, sz in sub_sizes.items():
        print(f"  分包 {s:<14} {mb(sz):7.2f} MB   (单包限制 20.00)")
    print(f"  总计:   {mb(total):7.2f} MB   (限制 20.00)   {'OK' if total <= TOTAL_LIMIT else '超限 ' + f'{mb(total - TOTAL_LIMIT):.2f} MB'}")

    if total > TOTAL_LIMIT:
        print("\n  超出部分最大来源（前 10 个文件）：")
        files = []
        for dp, _, fns in os.walk(GAME_DIR):
            for fn in fns:
                fp = os.path.join(dp, fn)
                files.append((os.path.getsize(fp), os.path.relpath(fp, GAME_DIR)))
        files.sort(reverse=True)
        for sz, p in files[:10]:
            print(f"    {mb(sz):7.2f} MB  {p}")

    return 0 if (main_size <= MAIN_LIMIT and total <= TOTAL_LIMIT) else 1


if __name__ == "__main__":
    sys.exit(main())
