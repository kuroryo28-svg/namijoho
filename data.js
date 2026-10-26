const DATA = {
  "pair": "USD/JPY",
  "rate": "157.54",
  "stamp": "10/27 (火) 08:59 JST",
  "condition": "ふつう",
  "note": "朝から動く。21時から上がる。金に大きいのが来る。",
  "size_pips": 70,
  "size_vs_norm": "平年比 1.0",
  "face": "ぐちゃぐちゃ",
  "face_sub": "ヒゲだらけ・入らない方が",
  "best": "21–24時",
  "best_sub": "NY 重複",
  "hourly": [
    76,
    61,
    54,
    56,
    47,
    42,
    51,
    48,
    55,
    87,
    78,
    69,
    56,
    56,
    60,
    80,
    81,
    81,
    70,
    61,
    68,
    100,
    93,
    93
  ],
  "best_from": 21,
  "best_to": 24,
  "norm_line": 68,
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
      "tag": "織り込み進行",
      "cls": "t-in",
      "when": "10/26",
      "text": "FX/為替「ドル/円今日の見通し｜157円台半ばへ上昇 関心は日米金融政策に」 外為どっとコム トゥデイ"
    },
    {
      "tag": "小さめ",
      "cls": "t-min",
      "when": "10/26",
      "text": "東京外国為替市場概況・8時 ドル円、小動き(トレーダーズ・ウェブ)"
    },
    {
      "tag": "大うねり",
      "cls": "t-big",
      "when": "10/26",
      "text": "東京為替見通し＝ドル円、9月企業向けサービス価格指数と特殊要因除くコアCPIに注目(トレーダーズ・ウェブ"
    },
    {
      "tag": "上は風が強い",
      "cls": "t-wind",
      "when": "10/26",
      "text": "ドル円157円台でもみ合い、FOMC・日銀会合を前に様子見 米AI株安が円買い圧力"
    }
  ],
  "week": [
    {
      "d": "水",
      "date": "10/28",
      "size": 83,
      "lo": 48,
      "hi": 113,
      "c": "ふつう"
    },
    {
      "d": "木",
      "date": "10/29",
      "size": 78,
      "lo": 64,
      "hi": 115,
      "c": "ふつう"
    },
    {
      "d": "金",
      "date": "10/30",
      "size": 85,
      "lo": 59,
      "hi": 111,
      "c": "いい"
    },
    {
      "d": "月",
      "date": "11/2",
      "size": 92,
      "lo": 57,
      "hi": 126,
      "c": "いい"
    },
    {
      "d": "火",
      "date": "11/3",
      "size": 96,
      "lo": 62,
      "hi": 142,
      "c": "いい"
    }
  ],
  "forecast_abstain": true,
  "forecast_reason": "似た並びが過去にない",
  "diag": {
    "library": 507,
    "k": 30,
    "d_k": 10.526,
    "d_k_pct": 91.9,
    "spread": 0.19,
    "oldest": 13,
    "newest": 503,
    "random_med": [
      90,
      95,
      98,
      124,
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
  "tokyo_pips": 58,
  "tokyo_ratio": 0.61,
  "tokyo_ratio_median": 0.45,
  "control_board": "HANABI",
  "recent_actual": [
    {
      "date": "10/16",
      "d": "金",
      "pips": 48
    },
    {
      "date": "10/19",
      "d": "月",
      "pips": 80
    },
    {
      "date": "10/20",
      "d": "火",
      "pips": 71
    },
    {
      "date": "10/21",
      "d": "水",
      "pips": 54
    },
    {
      "date": "10/22",
      "d": "木",
      "pips": 155
    },
    {
      "date": "10/23",
      "d": "金",
      "pips": 105
    },
    {
      "date": "10/26",
      "d": "月",
      "pips": 19
    }
  ],
  "review": [
    {
      "date": "10/19",
      "d": "月",
      "pred": 98,
      "lo": 48,
      "hi": 122,
      "actual": 80,
      "label": "ドンピシャ",
      "points": 100,
      "from": "10/16"
    },
    {
      "date": "10/19",
      "d": "月",
      "pred": 107,
      "lo": 68,
      "hi": 135,
      "actual": 80,
      "label": "当たり",
      "points": 85,
      "from": "10/17"
    },
    {
      "date": "10/21",
      "d": "水",
      "pred": 83,
      "lo": 48,
      "hi": 112,
      "actual": 54,
      "label": "当たり",
      "points": 85,
      "from": "10/20"
    },
    {
      "date": "10/22",
      "d": "木",
      "pred": 80,
      "lo": 48,
      "hi": 113,
      "actual": 155,
      "label": "外し",
      "points": 25,
      "from": "10/21"
    },
    {
      "date": "10/23",
      "d": "金",
      "pred": 87,
      "lo": 48,
      "hi": 122,
      "actual": 105,
      "label": "当たり",
      "points": 85,
      "from": "10/22"
    },
    {
      "date": "10/26",
      "d": "月",
      "pred": 80,
      "lo": 56,
      "hi": 102,
      "actual": 19,
      "label": "大外し",
      "points": 10,
      "from": "10/23"
    },
    {
      "date": "10/26",
      "d": "月",
      "pred": 83,
      "lo": 48,
      "hi": 113,
      "actual": 19,
      "label": "大外し",
      "points": 10,
      "from": "10/24"
    }
  ],
  "review_avg": 57,
  "selector_revision": 1,
  "sel_rule_version": "SEL-v1",
  "scoring_version": "v1",
  "sel_recommended_board": "HANABI",
  "neighbor_distance": 10.526,
  "neighbor_distance_pct": 91.9,
  "neighbor_k": 30,
  "abstained": true,
  "generated_at": "2026-10-26T23:59:18.128417+00:00"
};
