#!/usr/bin/env python3
"""
data.js を作る。標準ライブラリのみ。外部データは自分で取りに行く。

    python3 make_data.py

取得元:
    価格   Yahoo Finance chart API（JPY=X）… 日足2年 + 5分足60日
    ニュース Google ニュース RSS（fetch_news.py）
    週間   価格履歴からアナログ探索（forecast.py）
"""

import sys, json, statistics as st
import datetime as dt
import urllib.request
from pathlib import Path

import fetch_news
import forecast as fc

SYMBOL = "JPY=X"
PIP = 0.01
TZ_SHIFT = 9          # UTC -> JST
LOOKBACK_DAYS = 60    # 時間帯プロファイル（5分足の取得上限）
NORM_DAYS = 250
RECENT_DAYS = 20
UA = "Mozilla/5.0 (obanzak-namijoho/0.1)"
WD = "月火水木金土日"

# --- しきい値。動かす前に決めて、決めたら触らない ---
COND_LOW, COND_HIGH = 0.75, 1.15
FACE_CLEAN, FACE_ROUGH = 1.8, 3.0


# ---------------------------------------------------------------- 価格
def yahoo(interval, rng):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}"
           f"?interval={interval}&range={rng}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.load(r)
    res = j["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    bars = []
    for i, ts in enumerate(res["timestamp"]):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c):
            continue
        bars.append({
            "jst": dt.datetime.utcfromtimestamp(ts) + dt.timedelta(hours=TZ_SHIFT),
            "o": o, "h": h, "l": l, "c": c,
        })
    if not bars:
        raise RuntimeError(f"バーが取れない ({interval}/{rng})")
    return bars


def hourly_profile(m5):
    buckets = {h: [] for h in range(24)}
    for b in m5:
        buckets[b["jst"].hour].append((b["h"] - b["l"]) / PIP)
    prof = []
    for h in range(24):
        prof.append(st.mean(buckets[h]) if buckets[h] else 0.0)
    top = max(prof) or 1.0
    return [round(v / top * 100) for v in prof], prof


def best_window(prof):
    best_i, best_v = 0, -1.0
    for i in range(22):
        v = sum(prof[i:i + 3])
        if v > best_v:
            best_i, best_v = i, v
    return best_i, best_i + 3


def label_condition(r):
    return "凪" if r < COND_LOW else ("ふつう" if r < COND_HIGH else "いい")


def label_face(w):
    if w < FACE_CLEAN: return "きれい", "実体が出てる・続く"
    if w < FACE_ROUGH: return "荒れ気味", "ヒゲ多め・続かない"
    return "ぐちゃぐちゃ", "ヒゲだらけ・入らない方が"


def pick_board(cond, w):
    if cond == "凪":     return "入らない", "波がない。今日は寝る"
    if w >= FACE_CLEAN:  return "HANABI", "掘れて速い。長く乗る日ではない"
    return "WATERMAN", "小さいが面がいい。長く乗れる"


def session_name(h):
    if 9 <= h < 16:  return "東京"
    if 16 <= h < 21: return "ロンドン"
    if 21 <= h < 24: return "NY 重複"
    return "NY 後半"


# ---------------------------------------------------------------- 週間
def build_week(fcst, today):
    """予報を曜日ラベルに乗せる"""
    days, d = [], today
    while len(days) < len(fcst["days"]):
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            days.append(d)
    out = []
    for d, f in zip(days, fcst["days"]):
        med = round(f["med"])
        out.append({
            "d": WD[d.weekday()],
            "date": f"{d.month}/{d.day}",
            "size": med,
            "lo": round(f["lo"]),
            "hi": round(f["hi"]),
            "c": label_condition(med / NORMAL_REF[0] if NORMAL_REF[0] else 1.0),
        })
    return out


NORMAL_REF = [0.0]


def build_note(prof, b_from, week):
    avg = st.mean(prof) or 1.0
    morning = st.mean(prof[6:11])
    parts = ["朝は凪" if morning < avg * 0.8 else "朝から動く"]
    parts.append(f"{b_from}時から上がる" if b_from >= 15 else f"{b_from}時が山")
    big = [w for w in week if w.get("c") == "いい"]
    if big:
        parts.append(f"{big[0]['d']}に大きいのが来る")
    return "。".join(parts) + "。"


# ---------------------------------------------------------------- main
def main():
    print("  価格取得中…", file=sys.stderr)
    d1 = yahoo("1d", "2y")
    m5 = yahoo("5m", f"{LOOKBACK_DAYS}d")

    rng = [(b["h"] - b["l"]) / PIP for b in d1]
    body = [abs(b["c"] - b["o"]) / PIP for b in d1]

    recent = st.median(rng[-RECENT_DAYS:])
    normal = st.median(rng[-NORM_DAYS:])
    ratio = recent / normal if normal else 1.0
    wick = (st.median([r - b for r, b in zip(rng[-RECENT_DAYS:], body[-RECENT_DAYS:])])
            / max(st.median(body[-RECENT_DAYS:]), 1e-9))

    hourly, prof = hourly_profile(m5)
    b_from, b_to = best_window(prof)
    cond = label_condition(ratio)
    face, face_sub = label_face(wick)
    board, reason = pick_board(cond, wick)

    now = m5[-1]["jst"]

    NORMAL_REF[0] = normal
    print("  予報を組み立て中…", file=sys.stderr)
    fcst = fc.run(d1, PIP)
    week = build_week(fcst, now.date())

    print("  ニュース取得中…", file=sys.stderr)
    try:
        sources = fetch_news.collect()
    except Exception as e:
        print(f"  ニュース取得失敗: {e}", file=sys.stderr)
        sources = []

    data = {
        "pair": "USD/JPY",
        "rate": f"{m5[-1]['c']:.2f}",
        "stamp": f"{now.month}/{now.day} ({WD[now.weekday()]}) {now:%H:%M} JST",
        "condition": cond,
        "note": build_note(prof, b_from, week),
        "size_pips": round(recent),
        "size_vs_norm": f"平年比 {ratio:.1f}",
        "face": face,
        "face_sub": face_sub,
        "best": f"{b_from}–{b_to}時",
        "best_sub": session_name(b_from),
        "hourly": hourly,
        "best_from": b_from,
        "best_to": b_to,
        "norm_line": round(st.mean(prof) / max(prof) * 100),
        "sessions": [
            {"label": "東京",     "on": 9 <= b_from < 16},
            {"label": "ロンドン", "on": 16 <= b_from < 21},
            {"label": "NY 重複",  "on": 21 <= b_from < 24},
            {"label": "NY 後半",  "on": b_from < 9},
        ],
        "sources": sources,
        "week": week,
        "forecast_abstain": fcst["abstain"],
        "forecast_reason": fcst["reason"],
        "diag": fcst["diag"],
        "pick": {"name": board, "reason": reason},
        "boards": ["HANABI", "WATERMAN"],
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }

    Path("data.js").write_text(
        "const DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8")
    tail = "棄権" if fcst["abstain"] else f"予報{len(week)}日"
    print(f"data.js  {cond} / {round(recent)}pips / {board} / "
          f"ニュース{len(sources)}件 / {tail}")


if __name__ == "__main__":
    main()
