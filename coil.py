#!/usr/bin/env python3
"""
溜まり（coil）— 前日までに確定している2つの生値。

大勝ちした日の直前に共通していた形を、そのまま数値にしただけのもの。

  前日終値位置   前日の終値が、その日のレンジのどこで終わったか（0=安値引け）
  前3日純変化    直前3営業日の純変化を ATR14 で割ったもの（符号つき）

観測の出どころ:
  日次損益 上位20日 vs その他286日
    前日終値位置   0.412 vs 0.596   （前半・後半とも同方向）
    前3日純変化   +0.207 vs +3.379  （前半・後半とも同方向）

  溜まってから放たれる、という形。上がった後ではない。

ここで守っていること:

  * 合成しない。2つを1つの点数にまとめない。まとめると中で何が
    効いているか分からなくなる（Brain B で一度やって失敗している）
  * ラベルにしない。生値と百分位だけを出す。「高い/低い」の判定は
    見る側がやる
  * 推奨に使わない。SEL-v1 の入力にしない。これは表示だけの項目
  * 当日以降の価格を一切使わない。前日の終値までで確定する

版が上がったら過去の値と混ぜないこと。
"""

import datetime as dt
import statistics as st

COIL_VERSION = "coil-v0"

ATR_WIN = 14      # ATR の本数（日足）
NET_DAYS = 3      # 純変化を見る営業日数
PCT_WIN = 250     # 百分位を取る履歴の長さ


# ------------------------------------------------------------ 完成足
def completed(d1, today_utc=None):
    """
    進行中の当日足を落とす。

    Yahoo の日足は当日ぶんが未確定のまま最後に入る。UTC の日付が
    今日以降のバーは落とす。JST 変換済み（+9h）のバーは日付が
    UTC 日付と一致する。
    """
    if today_utc is None:
        today_utc = dt.datetime.now(dt.timezone.utc).date()
    return [b for b in d1 if b["jst"].date() < today_utc]


# ------------------------------------------------------------ ATR
def atr_series(bars, pip=0.01, win=ATR_WIN):
    """各バー時点の ATR（pips）。前 win 本の真の値幅の平均"""
    tr = []
    for i, b in enumerate(bars):
        if i == 0:
            tr.append((b["h"] - b["l"]) / pip)
            continue
        pc = bars[i - 1]["c"]
        tr.append(max(b["h"] - b["l"], abs(b["h"] - pc), abs(b["l"] - pc)) / pip)

    out = []
    for i in range(len(bars)):
        w = tr[max(0, i - win + 1): i + 1]
        out.append(st.mean(w) if w else None)
    return out


# ------------------------------------------------------------ 2つの生値
def close_position(bar):
    """終値がその日のレンジのどこか。0=安値引け, 1=高値引け"""
    span = bar["h"] - bar["l"]
    if span <= 0:
        return None
    return (bar["c"] - bar["l"]) / span


def net_change_atr(bars, i, atr, days=NET_DAYS):
    """
    i 本目を最終日とする days 営業日の純変化を ATR で割る。

        (最終日の終値 - 初日の始値) / ATR
    """
    j = i - days + 1
    if j < 0 or atr[i] in (None, 0):
        return None
    return (bars[i]["c"] - bars[j]["o"]) / 0.01 / atr[i]


# ------------------------------------------------------------ 百分位
def percentile_of(series, x, win=PCT_WIN):
    """履歴の中で x が下から何%の位置にいるか"""
    hist = [v for v in series[-win:] if v is not None]
    if not hist or x is None:
        return None
    return round(sum(1 for v in hist if v <= x) / len(hist) * 100, 1)


# ------------------------------------------------------------ 組み立て
def build(d1, pip=0.01, today_utc=None):
    """
    戻り値（値が取れなければ None を入れる。推測で埋めない）:

      {
        version, as_of,            使った前日の日付
        close_position,            生値 0..1
        close_position_pct,        百分位
        net3d_atr,                 生値（符号つき、ATR 単位）
        net3d_atr_pct,             百分位
        atr_pips,                  分母に使った ATR
        n_history,                 百分位に使った本数
      }
    """
    bars = completed(d1, today_utc)
    if len(bars) < NET_DAYS + ATR_WIN:
        return {"version": COIL_VERSION, "as_of": None,
                "close_position": None, "close_position_pct": None,
                "net3d_atr": None, "net3d_atr_pct": None,
                "atr_pips": None, "n_history": 0,
                "reason": "日足が足りない"}

    atr = atr_series(bars, pip)

    cp_hist = [close_position(b) for b in bars]
    net_hist = [net_change_atr(bars, i, atr) for i in range(len(bars))]

    last = len(bars) - 1
    cp = cp_hist[last]
    net = net_hist[last]

    return {
        "version": COIL_VERSION,
        "as_of": bars[last]["jst"].date().isoformat(),
        "close_position": round(cp, 3) if cp is not None else None,
        "close_position_pct": percentile_of(cp_hist[:-1], cp),
        "net3d_atr": round(net, 2) if net is not None else None,
        "net3d_atr_pct": percentile_of(net_hist[:-1], net),
        "atr_pips": round(atr[last], 1) if atr[last] else None,
        "n_history": len([v for v in cp_hist[:-1][-PCT_WIN:] if v is not None]),
    }
