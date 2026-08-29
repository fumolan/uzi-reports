#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数成分股数据生成器 — 拉同花顺扶摇API, 生成 indices/*.json 供 indices.html 使用
权重口径: 成分股当日成交额占指数成分总成交额比例(资金热度权重, 游资视角)
用法: python3 scripts/build_indices.py   (key 从环境变量 HITHINK_FINANCE_API_KEY 或 ../apikey/tonghuashun.txt)
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime

API = "https://fuyao.aicubes.cn/api"
INDICES = [
    ("000016.SH", "上证50"),
    ("000300.SH", "沪深300"),
    ("886090.TI", "智谱AI概念"),
    ("881121.TI", "半导体"),
    ("881130.TI", "计算机设备"),
    ("884296.TI", "横向通用软件"),
    ("881155.TI", "银行"),
    ("884249.TI", "国有大型银行"),
    ("881125.TI", "汽车整车"),
    ("881281.TI", "电池"),
    ("881275.TI", "游戏"),
]
TOP_N = 60  # 每个指数保留成交额前N


def get_key():
    k = os.environ.get("HITHINK_FINANCE_API_KEY")
    if k:
        return k.strip()
    for p in [os.path.expanduser("~/claude/apikey/tonghuashun.txt")]:
        if os.path.exists(p):
            return open(p).read().strip()
    sys.exit("未找到扶摇API key")


def gh(path, params, key):
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"X-api-key": key, "User-Agent": "idx-builder"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    if d.get("code") != 0:
        raise RuntimeError(f"{path}: {d.get('message')}")
    return d["data"]


def build(code, name, key):
    cons = gh("/a-share-index/constituents/ths-stock-list", {"thscode": code}, key)["item"]
    codes = [c["thscode"] for c in cons]
    names = {c["thscode"]: c["name"] for c in cons}
    quotes = []
    for i in range(0, len(codes), 90):
        part = gh("/a-share/prices/snapshot", {"thscodes": ",".join(codes[i:i+90])}, key)["item"]
        quotes.extend(part)
    total_to = sum(q.get("turnover") or 0 for q in quotes)
    stocks = []
    for q in quotes:
        to = q.get("turnover") or 0
        stocks.append({
            "c": q["thscode"], "n": names.get(q["thscode"], q["thscode"]),
            "p": q.get("last_price"), "chg": round(q.get("price_change_ratio_pct") or 0, 2),
            "w": round(to / total_to * 100, 2) if total_to else 0,
        })
    stocks.sort(key=lambda s: -s["w"])
    return {"code": code, "name": name, "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "count": len(cons), "weight_basis": "当日成交额占比(资金热度口径)",
            "stocks": stocks[:TOP_N]}


def main():
    key = get_key()
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(repo, "indices")
    os.makedirs(out_dir, exist_ok=True)
    catalog = []
    for code, name in INDICES:
        d = build(code, name, key)
        fn = f"{code.split('.')[0]}.json"
        json.dump(d, open(os.path.join(out_dir, fn), "w"), ensure_ascii=False, indent=1)
        catalog.append({"code": code, "name": name, "file": f"indices/{fn}",
                        "updated": d["updated"], "count": d["count"]})
        print(f"✓ {name}({code}): {d['count']}只成分, 保留前{len(d['stocks'])}, "
              f"榜首 {d['stocks'][0]['n']} {d['stocks'][0]['w']}%")
    json.dump({"updated": datetime.now().strftime("%Y-%m-%d %H:%M"), "indices": catalog},
              open(os.path.join(out_dir, "index.json"), "w"), ensure_ascii=False, indent=1)
    print(f"✅ indices/index.json 共{len(catalog)}个指数")


if __name__ == "__main__":
    main()
