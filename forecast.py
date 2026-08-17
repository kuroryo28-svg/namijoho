#!/usr/bin/env python3
"""
波予報エンジン。過去の似た並びを探して、翌5営業日の波高を出す。

方式と、その制約
  - 特徴量は3種 × 直近5営業日 = 15次元。増やすと距離が意味を失う
  - 近傍 k=30。ただし10営業日以内の近傍は同一事象とみなして間引く
  - 似た並びが無い日は予報を出さない（棄権）
  - ランダム近傍30本の予報を常に並走させる。差が出なければ
    アナログ機構は効いていない。diag.random_* がその記録
  - 方向は出さない。波高だけ
"""

import random
import statistics as st

LOOKBACK = 5        # 過去何営業日を1つの並びとするか
HORIZON = 5         # 何営業日先まで予報するか
K = 30              # 近傍数
MIN_GAP = 10        # 近傍どうしの最小間隔（営業日）
PURGE = HORIZON * 2 # 直近この日数の窓は近傍に使わない
NORM_WIN = 60       # 特徴量の正規化に使う期間
ABSTAIN_PCT = 90    # 近傍距離がこの百分位を超えたら棄権
SEED = 20260817     # ランダム近傍の種。固定


def _median(xs):
    return st.median(xs) if xs else 0.0


def build_features(daily, pip=0.01):
    """日足から (特徴量行列, 波高列) を作る"""
    rng = [(b["h"] - b["l"]) / pip for b in daily]
    body = [abs(b["c"] - b["o"]) / pip for b in daily]
    ret = [0.0] + [abs(daily[i]["c"] - daily[i - 1]["c"]) / pip
                   for i in range(1, len(daily))]

    rn, br, ar = [], [], []
    for i in range(len(daily)):
        lo = max(0, i - NORM_WIN)
        m_rng = _median(rng[lo:i + 1]) or 1.0
        m_ret = _median(ret[lo:i + 1]) or 1.0
        rn.append(rng[i] / m_rng)
        br.append(body[i] / rng[i] if rng[i] else 0.0)
        ar.append(ret[i] / m_ret)

    return {"rng": rng, "rn": rn, "br": br, "ar": ar}


def vector(f, i):
    """i 日目で終わる並びの特徴ベクトル"""
    s = i - LOOKBACK + 1
    if s < 0:
        return None
    return f["rn"][s:i + 1] + f["br"][s:i + 1] + f["ar"][s:i + 1]


def zstats(vecs):
    dims = len(vecs[0])
    mu, sd = [], []
    for d in range(dims):
        col = [v[d] for v in vecs]
        m = st.mean(col)
        s = st.pstdev(col) or 1.0
        mu.append(m); sd.append(s)
    return mu, sd


def z(v, mu, sd):
    return [(v[d] - mu[d]) / sd[d] for d in range(len(v))]


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def neighbors(qz, lib, exclude_after):
    """距離順に並べ、MIN_GAP で間引いて K 本返す"""
    scored = sorted(
        ((dist(qz, v), i) for i, v in lib if i <= exclude_after),
        key=lambda t: t[0])
    picked = []
    for d, i in scored:
        if any(abs(i - j) < MIN_GAP for _, j in picked):
            continue
        picked.append((d, i))
        if len(picked) >= K:
            break
    return picked


def targets(f, i):
    """i 日目で終わる並びの、翌 HORIZON 営業日の波高"""
    return f["rng"][i + 1:i + 1 + HORIZON]


def run(daily, pip=0.01):
    f = build_features(daily, pip)
    n = len(daily)
    last = n - 1

    # 予報対象が揃っている窓だけを図書館に入れる
    lib_raw = []
    for i in range(LOOKBACK - 1, n - HORIZON):
        v = vector(f, i)
        if v:
            lib_raw.append((i, v))
    if len(lib_raw) < K * 3:
        return {"abstain": True, "reason": "履歴が足りない",
                "days": [], "diag": {"library": len(lib_raw)}}

    mu, sd = zstats([v for _, v in lib_raw])
    lib = [(i, z(v, mu, sd)) for i, v in lib_raw]

    qv = vector(f, last)
    qz = z(qv, mu, sd)
    cutoff = last - PURGE

    picked = neighbors(qz, lib, cutoff)
    if len(picked) < K:
        return {"abstain": True, "reason": "近傍が足りない",
                "days": [], "diag": {"picked": len(picked)}}

    dK = picked[-1][0]

    # 過去の各時点でも同じことをやって、dK の分布を作る（棄権判定用）
    hist = []
    step = max(1, len(lib) // 200)
    for idx in range(K * 3, len(lib), step):
        i, v = lib[idx]
        p = neighbors(v, lib, i - PURGE)
        if len(p) >= K:
            hist.append(p[-1][0])
    hist.sort()
    pct = 100.0 * sum(1 for h in hist if h < dK) / len(hist) if hist else 0.0
    abstain = pct > ABSTAIN_PCT

    # 予報
    days = []
    for j in range(HORIZON):
        vals = sorted(targets(f, i)[j] for _, i in picked
                      if len(targets(f, i)) > j)
        if not vals:
            break
        days.append({
            "med": _median(vals),
            "lo": vals[int(len(vals) * 0.25)],
            "hi": vals[int(len(vals) * 0.75)],
        })

    # ランダム近傍（対照群）。ここに勝てないならアナログは効いていない
    rnd = random.Random(SEED)
    pool = [i for i, _ in lib if i <= cutoff]
    rsel = rnd.sample(pool, min(K, len(pool)))
    rnd_days = []
    for j in range(len(days)):
        vals = [targets(f, i)[j] for i in rsel if len(targets(f, i)) > j]
        rnd_days.append(_median(vals) if vals else 0.0)

    span = [i for _, i in picked]
    spread = st.pstdev([d for d, _ in picked]) / (_median([d for d, _ in picked]) or 1.0)

    return {
        "abstain": abstain,
        "reason": "似た並びが過去にない" if abstain else "",
        "days": days,
        "diag": {
            "library": len(lib),
            "k": K,
            "d_k": round(dK, 3),
            "d_k_pct": round(pct, 1),
            "spread": round(spread, 3),
            "oldest": min(span),
            "newest": max(span),
            "random_med": [round(x) for x in rnd_days],
        },
    }
