#!/usr/bin/env python3
"""
ニュース取得。Google ニュース RSS を叩いて「うねりの元」に整形する。
API キー不要。個人利用のフィードリーダー用途の範囲で使う。

    python3 fetch_news.py          # 単体で動作確認
"""

import re, sys, json, html
import datetime as dt
import urllib.parse, urllib.request
import xml.etree.ElementTree as ET

# 拾うクエリ。when:7d で直近7日に絞る。
QUERIES = [
    "日銀 利上げ when:7d",
    "ドル円 為替 when:5d",
    "為替介入 財務省 when:14d",
    "FOMC 米金利 when:7d",
]

MAX_ITEMS = 4
UA = "Mozilla/5.0 (obanzak-namijoho/0.1)"

# タグ分類。上から順にマッチした最初のものを採用する。
# 語彙はここだけ。増やすときは4種の枠内で。
RULES = [
    ("t-wind", "上は風が強い", ["介入", "財務相", "財務省", "口先", "円買い", "ベッセント", "為替当局"]),
    ("t-big",  "大うねり",     ["決定会合", "FOMC", "利上げ", "政策金利", "総裁", "雇用統計", "CPI", "消費者物価"]),
    ("t-in",   "織り込み進行", ["織り込", "OIS", "確率", "予想", "見通し", "観測"]),
]
DEFAULT = ("t-min", "小さめ")


def feed_url(q):
    return ("https://news.google.com/rss/search?q="
            + urllib.parse.quote(q)
            + "&hl=ja&gl=JP&ceid=JP:ja")


def fetch(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def clean(title):
    """Google が付ける ' - 媒体名' の尻尾を落とす"""
    t = html.unescape(title)
    t = re.sub(r"\s+-\s+[^-]+$", "", t).strip()
    return t


def classify(text):
    for cls, tag, words in RULES:
        if any(w in text for w in words):
            return cls, tag
    return DEFAULT


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    out = []
    for item in root.iter("item"):
        title = item.findtext("title") or ""
        pub = item.findtext("pubDate") or ""
        try:
            when = dt.datetime.strptime(pub[:25].strip(), "%a, %d %b %Y %H:%M:%S")
        except ValueError:
            when = dt.datetime.utcnow()
        out.append({"title": clean(title), "when": when})
    return out


def norm(s):
    return re.sub(r"[\s　「」【】（）()]", "", s)[:16]


def collect():
    seen, items = set(), []
    for q in QUERIES:
        try:
            raw = fetch(feed_url(q))
        except Exception as e:
            print(f"  取得失敗 [{q}]: {e}", file=sys.stderr)
            continue
        for it in parse(raw):
            k = norm(it["title"])
            if k in seen or not k:
                continue
            seen.add(k)
            items.append(it)

    items.sort(key=lambda x: x["when"], reverse=True)

    # 4枠。同じタグで埋まらないよう、種類ごとに最新1本を先に確保する。
    picked, used_cls = [], set()
    for it in items:
        cls, tag = classify(it["title"])
        if cls in used_cls:
            continue
        used_cls.add(cls)
        picked.append((it, cls, tag))
        if len(picked) >= MAX_ITEMS:
            break
    for it in items:
        if len(picked) >= MAX_ITEMS:
            break
        if any(p[0] is it for p in picked):
            continue
        cls, tag = classify(it["title"])
        picked.append((it, cls, tag))

    return [{
        "tag": tag,
        "cls": cls,
        "when": f"{it['when'].month}/{it['when'].day}",
        "text": it["title"][:52],
    } for it, cls, tag in picked[:MAX_ITEMS]]


if __name__ == "__main__":
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
