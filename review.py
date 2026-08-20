#!/usr/bin/env python3
"""
過去の予報アーカイブと実測を突き合わせて採点する。

forecasts/YYYY-MM-DD.json をそのまま読み、当日ぶんの予報値と
実際の日足レンジを比べる。予報の遡及生成はしない。
アーカイブが無い日は単に行が出ないだけ。
"""

import json
import datetime as dt
from pathlib import Path

import selector as sel

ARCHIVE_DIR = Path("forecasts")
WD = "月火水木金土日"


def load_archives(limit=14):
    """新しい順にアーカイブを読む"""
    if not ARCHIVE_DIR.exists():
        return []
    out = []
    for p in sorted(ARCHIVE_DIR.glob("*.json"), reverse=True)[:limit]:
        try:
            out.append((p.stem, json.loads(p.read_text(encoding="utf-8"))))
        except Exception:
            continue
    return out


def actual_ranges(daily, pip=0.01):
    """日足バーから 日付 -> レンジpips の辞書"""
    return {b["jst"].date(): (b["h"] - b["l"]) / pip for b in daily}


def build_review(daily, days=7):
    """
    直近 days 営業日ぶんの「予報 vs 実測 + 点数」。
    アーカイブがある日だけ行が出る。溜まるまで行数は増えない。
    """
    actual = actual_ranges(daily)
    rows = []

    for stem, data in load_archives(limit=days * 3):
        try:
            d = dt.date.fromisoformat(stem)
        except ValueError:
            continue

        # その日の予報における「当日ぶん」は week[0] ではなく
        # 予報作成時点の size_pips（当日の実況）ではなく、
        # 前日以前に出された当日の予報を使う必要がある。
        # ここでは archive 自身が持つ翌営業日ぶん week[0] を
        # 「その予報が指した最初の日」として扱う。
        wk = data.get("week") or []
        if not wk:
            continue
        first = wk[0]

        target = None
        for off in range(1, 5):
            cand = d + dt.timedelta(days=off)
            if cand.weekday() < 5:
                target = cand
                break
        if target is None or target not in actual:
            continue

        sc = sel.score_forecast(first.get("size"), first.get("lo"),
                                first.get("hi"), actual[target])
        if sc is None:
            continue

        rows.append({
            "date": f"{target.month}/{target.day}",
            "d": WD[target.weekday()],
            "pred": first.get("size"),
            "lo": first.get("lo"),
            "hi": first.get("hi"),
            "actual": round(actual[target]),
            "label": sc["label"],
            "points": sc["points"],
            "from": f"{d.month}/{d.day}",
        })
        if len(rows) >= days:
            break

    rows.reverse()
    avg = round(sum(r["points"] for r in rows) / len(rows)) if rows else None
    return rows, avg


def build_recent_actual(daily, days=7, pip=0.01):
    """直近の実績波高。アーカイブ不要なので初日から出る"""
    out = []
    for b in daily[-days:]:
        d = b["jst"].date()
        out.append({
            "date": f"{d.month}/{d.day}",
            "d": WD[d.weekday()],
            "pips": round((b["h"] - b["l"]) / pip),
        })
    return out
