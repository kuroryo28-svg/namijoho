#!/usr/bin/env python3
"""
板の選択ルールと採点。

このファイルの定数は全て「仮置き」である。
根拠となる観測はまだ無い。26エポック後に候補ログで検証するまで、
結果を見て動かさないこと。動かす場合は revision を上げ、
それ以前の記録と混ぜないこと。

  SELECTOR_REVISION … 選択ルールの版。上げたら過去の推奨と比較しない
  SCORING_VERSION   … 採点定義の版。上げたら過去の点と混ぜない
"""

import hashlib
import statistics as st

SELECTOR_REVISION = 1
SEL_RULE_VERSION = "SEL-v1"
SCORING_VERSION = "v1"

BOARDS = ["HANABI", "WATERMAN", "NAGI"]

# --- 確信度の境界（d_k_pct）。小さいほど似た日が多い ---
CONF_HIGH = 33
CONF_LOW = 67

# --- 採点の段階。帯の端からの乖離率（%）と、名前・点 ---
SCORE_BANDS = [
    (0.0,  "ドンピシャ", 100),   # 帯の中央1/3
    (0.0,  "当たり",      85),   # 帯の中
    (10.0, "ニアミス",    70),
    (20.0, "惜しい",      55),
    (35.0, "かすった",    40),
    (50.0, "外し",        25),
    (75.0, "大外し",      10),
    (999.0, "逆走",        0),
]


# ------------------------------------------------------------ 確信度
def confidence_label(d_k_pct):
    """近傍距離の百分位を3段階に。生値は台帳へ残すこと"""
    if d_k_pct is None:
        return "不明"
    if d_k_pct < CONF_HIGH:
        return "高い"
    if d_k_pct > CONF_LOW:
        return "低い"
    return "ふつう"


# ------------------------------------------------------------ 東京レンジ
def tokyo_range_stats(m5, pip=0.01, window=20):
    """
    5分足から日ごとの東京時間(9-12時 JST)レンジと、日足レンジに対する比を出す。

    戻り値: (日付順のリスト, 直近windowの比の中央値)
      各要素 {date, tokyo_pips, daily_pips, ratio}
    """
    days = {}
    for b in m5:
        d = b["jst"].date()
        rec = days.setdefault(d, {"t_hi": None, "t_lo": None,
                                  "d_hi": None, "d_lo": None})
        h, l = b["h"], b["l"]
        rec["d_hi"] = h if rec["d_hi"] is None else max(rec["d_hi"], h)
        rec["d_lo"] = l if rec["d_lo"] is None else min(rec["d_lo"], l)
        if 9 <= b["jst"].hour < 12:
            rec["t_hi"] = h if rec["t_hi"] is None else max(rec["t_hi"], h)
            rec["t_lo"] = l if rec["t_lo"] is None else min(rec["t_lo"], l)

    out = []
    for d in sorted(days):
        r = days[d]
        if r["t_hi"] is None or r["d_hi"] is None:
            continue
        t = (r["t_hi"] - r["t_lo"]) / pip
        dl = (r["d_hi"] - r["d_lo"]) / pip
        if dl <= 0:
            continue
        out.append({"date": d, "tokyo_pips": t, "daily_pips": dl,
                    "ratio": t / dl})

    recent = [x["ratio"] for x in out[-window:]]
    med = st.median(recent) if recent else 0.0
    return out, med


# ------------------------------------------------------------ SEL-v1
def select_board(wave_tercile, confidence, abstained,
                 tokyo_ratio, tokyo_ratio_median, operational_hold=False):
    """
    朝の板選択ルール。全ての閾値は仮置き。

    wave_tercile … "high" / "mid" / "low"（波高の3分位）
    confidence   … "高い" / "ふつう" / "低い" / "不明"

    戻り値: (board, reason)
    """
    if operational_hold:
        return "置かない", "運用都合（メンテ・復旧）"

    if abstained or confidence == "低い" or confidence == "不明":
        return "HANABI", "予報が不確か。迷ったら空振りの安いほう"

    if wave_tercile == "high":
        return "HANABI", "波が大きい。掘れて速い日"

    if wave_tercile == "low" and confidence == "高い":
        return "WATERMAN", "小さいが確度が高い。長く乗れる"

    if (wave_tercile == "mid"
            and tokyo_ratio is not None
            and tokyo_ratio >= tokyo_ratio_median
            and confidence != "低い"):
        return "NAGI", "東京時間に値幅が出やすい。レンジの端を取る"

    return "HANABI", "どれにも当てはまらず。安いほうへ"


def wave_tercile(size_pips, history_pips):
    """波高が直近履歴の3分位のどこか"""
    if not history_pips:
        return "mid"
    s = sorted(history_pips)
    lo = s[len(s) // 3]
    hi = s[len(s) * 2 // 3]
    if size_pips >= hi:
        return "high"
    if size_pips <= lo:
        return "low"
    return "mid"


# ------------------------------------------------------------ サイコロ
def draw_control(date_str, seed_salt="obanzak-nami"):
    """
    対照群の板を引く。朝に引く。日付から決定的に決まるので再現可能。
    夕方に引き直しても同じ値になる（対照として成立させるため）。
    """
    h = hashlib.sha256(f"{seed_salt}:{date_str}".encode()).hexdigest()
    return BOARDS[int(h[:8], 16) % len(BOARDS)]


# ------------------------------------------------------------ 採点
def score_forecast(pred_med, pred_lo, pred_hi, actual):
    """
    予報と実測を突き合わせて8段階。定義は SCORING_VERSION で凍結。

    戻り値: {label, points, deviation_pct}
    """
    if actual is None or pred_lo is None or pred_hi is None:
        return None

    if pred_lo <= actual <= pred_hi:
        # 帯の中央1/3 に入っていれば最上位
        third = (pred_hi - pred_lo) / 3.0
        if pred_lo + third <= actual <= pred_hi - third:
            return {"label": "ドンピシャ", "points": 100, "deviation_pct": 0.0}
        return {"label": "当たり", "points": 85, "deviation_pct": 0.0}

    if actual > pred_hi:
        dev = (actual - pred_hi) / pred_hi * 100.0 if pred_hi else 999.0
    else:
        dev = (pred_lo - actual) / pred_lo * 100.0 if pred_lo else 999.0

    for limit, label, pts in SCORE_BANDS[2:]:
        if dev <= limit:
            return {"label": label, "points": pts,
                    "deviation_pct": round(dev, 1)}
    return {"label": "逆走", "points": 0, "deviation_pct": round(dev, 1)}
