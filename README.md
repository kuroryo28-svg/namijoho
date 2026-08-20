# 波情報 — USD/JPY

波の大きさ、面の質、時間帯だけを出す。上がるか下がるかは予報しない。

## デプロイ

1. GitHub で空のリポジトリを作る
2. このフォルダの中身をそのまま push

```bash
git init && git add . && git commit -m "初回"
git branch -M main
git remote add origin git@github.com:<user>/<repo>.git
git push -u origin main
```

3. **Settings → Pages → Source** を **GitHub Actions** に

以上。`https://<user>.github.io/<repo>/` に出る。
以降は平日 JST 5:30 に Actions が全部取り直して自動で更新される。
サーバーも API キーも要らない。

## 中身

| 項目 | どこから |
|---|---|
| レート・波高・面・時間帯 | Yahoo Finance chart API（`JPY=X`） |
| うねりの元（ニュース） | Google ニュース RSS |
| 波予報（翌5営業日） | 価格履歴からアナログ探索（`forecast.py`） |
| 東京レンジ・確信度 | 5分足から算出（`selector.py`） |
| 板の推奨（SEL-v1） | 選択ルール（`selector.py`） |
| 対照のサイコロ | 日付から決定的に生成（再現可能） |
| 予報の答え合わせ | `forecasts/` と実測の突合（`review.py`） |
| 判断ログ | ブラウザの localStorage |

## 板の選択について

**このアプリは推奨するだけで、決定はしない。** 選ぶのは人間。
推奨に従わなかった日も台帳に残る。従わなかった日が後で効いてくる。

選択肢は4つ。

    HANABI / WATERMAN / NAGI / 置かない

「置かない」は運用都合（メンテ・復旧）のときだけ。
**市場を理由に置かないことはしない。**「荒れすぎる日は入らない」には
実測の裏付けがないため。予報が棄権した日も置く。

### SEL-v1（全て仮置き）

    IF  運用都合                              → 置かない
    ELIF 予報が棄権 OR 確信度が低い            → HANABI
    ELIF 波高 上位1/3                          → HANABI
    ELIF 波高 下位1/3 AND 確信度が高い         → WATERMAN
    ELIF 波高 中位1/3 AND 東京レンジ比 ≥ 平常
         AND 確信度が低くない                  → NAGI
    ELSE                                       → HANABI

板ごとに要求する確信度が違う。HANABI は迷ったら出す（外しても空振りが安い）。
WATERMAN は確度が高い日だけ（広い SL で持っている最中に大波が来ると一番痛い）。

閾値と分位は**全て仮置き**。根拠となる観測はまだ無い。
26エポック後に候補ログで検証するまで、結果を見て動かさないこと。

## 採点（scoring_version = v1、凍結）

予報の帯（25〜75%）に対して実測がどこに落ちたかで8段階。

| 段階 | 点 | 条件 |
|---|---|---|
| ドンピシャ | 100 | 帯の中央1/3 |
| 当たり | 85 | 帯の中 |
| ニアミス | 70 | 帯の端から〜10% |
| 惜しい | 55 | 〜20% |
| かすった | 40 | 〜35% |
| 外し | 25 | 〜50% |
| 大外し | 10 | 〜75% |
| 逆走 | 0 | 75%超 |

定義を変えるときは `SCORING_VERSION` を上げ、それ以前の点と混ぜないこと。

## 予報アーカイブ

`forecasts/YYYY-MM-DD.json` に日次で予報の生データが append-only で溜まる。
同じ日のファイルは上書きされない。

**予報を過去に遡って生成することは禁止。** 遡及生成された予報は事後登録であり、
以後のあらゆる検定を無効化する。一度混入すると分離できない。

答え合わせは溜まった日数ぶんだけ出る。初日は0行、1週間で7行。

## 波予報のやり方と、その限界

過去2年の日足から「直近5営業日の並び」に似た過去の並びを探して、
その先で実際に何 pips 動いたかを集める。中央値が予報値、25〜75%が帯。

守ってること:

- 特徴量は3種（正規化レンジ・実体比・変化幅）× 5営業日 = 15次元だけ。
  増やすと距離が意味を失う
- 近傍 k=30。10営業日以内に固まってる近傍は同一事象として間引く
- 予報対象の期間と重なる窓は近傍に使わない
- 似た並びが過去に無い日は**予報を出さない**（画面に「予報なし」と出る）
- **ランダムに選んだ30本**の予報を常に並走させて画面下に出す。
  アナログ予報とランダムが同じ数字なら、似た日を選ぶ操作は効いていない

最後のがこの仕組みの生命線。毎日そこを見ること。

分かること: 波の大きさ、荒れ具合、動く時間帯。
分からないこと: 方向、水準、イベントで飛ぶ瞬間、転換点。

## 決め打ちの値

**結果を見てから動かさないこと。**

`forecast.py`
```
LOOKBACK=5  HORIZON=5  K=30  MIN_GAP=10  NORM_WIN=60  ABSTAIN_PCT=90
```

`selector.py`
```
SELECTOR_REVISION=1  SEL_RULE_VERSION="SEL-v1"  SCORING_VERSION="v1"
CONF_HIGH=33  CONF_LOW=67          # 確信度の境界（d_k_pct）
SCORE_BANDS                        # 採点の8段階
tokyo_range_stats(window=20)       # 東京レンジ比の基準期間
```

`make_data.py`
```
COND_LOW, COND_HIGH    = 0.75, 1.15
FACE_CLEAN, FACE_ROUGH = 1.8, 3.0
RECENT_DAYS=20  NORM_DAYS=250  LOOKBACK_DAYS=60
```

`fetch_news.py` の `RULES` も同じ。タグは4種類から増やさない。

## ファイル

```
index.html          画面。data.js だけ読む
data.js             生成物。Actions が上書きする
make_data.py        全体の組み立て
forecast.py         アナログ波予報エンジン
selector.py         板の選択ルール・確信度・採点・サイコロ
review.py           予報と実測の突合
fetch_news.py       ニュース取得とタグ分け
archive_forecast.py 予報の日次アーカイブ
forecasts/          予報の生データ（append-only）
.github/workflows/update.yml
```

## 注意

価格は Yahoo。研究で使っている Dukascopy とは別系統。
このアプリの数字を研究側の観測値として扱わないこと。
Yahoo の5分足は60日が上限なので、時間帯プロファイルは直近60日ぶんしかない。
