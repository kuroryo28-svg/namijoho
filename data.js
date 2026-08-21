const DATA = {
  "pair": "USD/JPY",
  "rate": "158.88",
  "stamp": "8/21 (金) 23:23 JST",
  "condition": "ふつう",
  "note": "朝から動く。21時から上がる。月に大きいのが来る。",
  "size_pips": 76,
  "size_vs_norm": "平年比 1.0",
  "face": "ぐちゃぐちゃ",
  "face_sub": "ヒゲだらけ・入らない方が",
  "best": "21–24時",
  "best_sub": "NY 重複",
  "hourly": [
    77,
    60,
    63,
    61,
    59,
    62,
    69,
    60,
    54,
    90,
    75,
    57,
    51,
    50,
    53,
    76,
    80,
    75,
    70,
    58,
    61,
    89,
    98,
    100
  ],
  "best_from": 21,
  "best_to": 24,
  "norm_line": 69,
  "sessions": [
    {
      "label": "東京",
      "on": false
    },
    {
      "label": "ロンドン",
      "on": false
    },
    {
      "label": "NY 重複",
      "on": true
    },
    {
      "label": "NY 後半",
      "on": false
    }
  ],
  "sources": [
    {
      "tag": "小さめ",
      "cls": "t-min",
      "when": "8/21",
      "text": "ドル円は１５８円台後半、一時のドル安が落ち着く＝ＮＹ為替序盤"
    },
    {
      "tag": "大うねり",
      "cls": "t-big",
      "when": "8/21",
      "text": "日銀、6月利上げ観測高まる"
    },
    {
      "tag": "織り込み進行",
      "cls": "t-in",
      "when": "8/21",
      "text": "NY為替見通し＝米超長期債の動向に注目、ドル売り・円売り地合いは変わらずか(トレーダーズ・ウェブ)"
    },
    {
      "tag": "上は風が強い",
      "cls": "t-wind",
      "when": "8/21",
      "text": "日銀の利上げ、ペース加速か インフレ上振れと日米協調介入が後押し"
    }
  ],
  "week": [
    {
      "d": "月",
      "date": "8/24",
      "size": 96,
      "lo": 68,
      "hi": 112,
      "c": "いい"
    },
    {
      "d": "火",
      "date": "8/25",
      "size": 101,
      "lo": 68,
      "hi": 134,
      "c": "いい"
    },
    {
      "d": "水",
      "date": "8/26",
      "size": 96,
      "lo": 60,
      "hi": 125,
      "c": "いい"
    },
    {
      "d": "木",
      "date": "8/27",
      "size": 96,
      "lo": 68,
      "hi": 145,
      "c": "いい"
    },
    {
      "d": "金",
      "date": "8/28",
      "size": 112,
      "lo": 88,
      "hi": 171,
      "c": "いい"
    }
  ],
  "forecast_abstain": true,
  "forecast_reason": "似た並びが過去にない",
  "diag": {
    "library": 509,
    "k": 30,
    "d_k": 7.845,
    "d_k_pct": 91.2,
    "spread": 0.1,
    "oldest": 11,
    "newest": 497,
    "random_med": [
      107,
      105,
      98,
      90,
      101
    ]
  },
  "pick": {
    "name": "HANABI",
    "reason": "予報が不確か。迷ったら空振りの安いほう"
  },
  "boards": [
    "HANABI",
    "WATERMAN",
    "NAGI"
  ],
  "confidence": "低い",
  "wave_tercile": "mid",
  "tokyo_pips": 27,
  "tokyo_ratio": 0.32,
  "tokyo_ratio_median": 0.38,
  "control_board": "HANABI",
  "coil": {
    "version": "coil-v0",
    "as_of": "2026-08-20",
    "close_position": 0.128,
    "close_position_pct": 17.2,
    "net3d_atr": -0.84,
    "net3d_atr_pct": 12.0,
    "atr_pips": 125.2,
    "n_history": 250
  },
  "coil_version": "coil-v0",
  "recent_actual": [
    {
      "date": "8/13",
      "d": "木",
      "pips": 45
    },
    {
      "date": "8/14",
      "d": "金",
      "pips": 86
    },
    {
      "date": "8/17",
      "d": "月",
      "pips": 55
    },
    {
      "date": "8/18",
      "d": "火",
      "pips": 46
    },
    {
      "date": "8/19",
      "d": "水",
      "pips": 148
    },
    {
      "date": "8/20",
      "d": "木",
      "pips": 78
    },
    {
      "date": "8/21",
      "d": "金",
      "pips": 79
    }
  ],
  "review": [
    {
      "date": "8/18",
      "d": "火",
      "pred": 84,
      "lo": 66,
      "hi": 120,
      "actual": 46,
      "label": "かすった",
      "points": 40,
      "from": "8/17"
    },
    {
      "date": "8/19",
      "d": "水",
      "pred": 98,
      "lo": 48,
      "hi": 122,
      "actual": 148,
      "label": "かすった",
      "points": 40,
      "from": "8/18"
    },
    {
      "date": "8/20",
      "d": "木",
      "pred": 91,
      "lo": 68,
      "hi": 107,
      "actual": 78,
      "label": "当たり",
      "points": 85,
      "from": "8/19"
    },
    {
      "date": "8/21",
      "d": "金",
      "pred": 89,
      "lo": 65,
      "hi": 121,
      "actual": 79,
      "label": "当たり",
      "points": 85,
      "from": "8/20"
    }
  ],
  "review_avg": 62,
  "selector_revision": 1,
  "sel_rule_version": "SEL-v1",
  "scoring_version": "v1",
  "sel_recommended_board": "HANABI",
  "neighbor_distance": 7.845,
  "neighbor_distance_pct": 91.2,
  "neighbor_k": 30,
  "abstained": true,
  "generated_at": "2026-08-21T14:23:21.126780+00:00"
};
