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
| 判断ログ | ブラウザの localStorage |

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

`make_data.py`
```
COND_LOW, COND_HIGH    = 0.75, 1.15
FACE_CLEAN, FACE_ROUGH = 1.8, 3.0
RECENT_DAYS=20  NORM_DAYS=250  LOOKBACK_DAYS=60
```

`fetch_news.py` の `RULES` も同じ。タグは4種類から増やさない。

## ファイル

```
index.html      画面。data.js だけ読む
data.js         生成物。Actions が上書きする
make_data.py    全体の組み立て
forecast.py     アナログ波予報エンジン
fetch_news.py   ニュース取得とタグ分け
.github/workflows/update.yml
```

## 注意

価格は Yahoo。研究で使っている Dukascopy とは別系統。
このアプリの数字を研究側の観測値として扱わないこと。
Yahoo の5分足は60日が上限なので、時間帯プロファイルは直近60日ぶんしかない。
