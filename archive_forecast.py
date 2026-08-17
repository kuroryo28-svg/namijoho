#!/usr/bin/env python3
"""data.js を forecasts/YYYY-MM-DD.json に append-only で保存する。"""
import json
import os
import re
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_JS = os.path.join(REPO_ROOT, "data.js")
FORECASTS_DIR = os.path.join(REPO_ROOT, "forecasts")


def load_data():
    with open(DATA_JS, encoding="utf-8") as f:
        text = f.read().strip()
    prefix = "const DATA = "
    if not text.startswith(prefix) or not text.endswith(";"):
        raise ValueError("data.js が想定した形式ではありません")
    return json.loads(text[len(prefix):-1])


def stamp_to_date(stamp):
    m = re.match(r"(\d{1,2})/(\d{1,2})", stamp)
    if not m:
        raise ValueError(f"stamp から日付を取り出せません: {stamp!r}")
    month, day = int(m.group(1)), int(m.group(2))
    year = datetime.now().year
    return f"{year:04d}-{month:02d}-{day:02d}"


def main():
    data = load_data()
    date_str = stamp_to_date(data["stamp"])
    os.makedirs(FORECASTS_DIR, exist_ok=True)
    out_path = os.path.join(FORECASTS_DIR, f"{date_str}.json")

    if os.path.exists(out_path):
        print(f"{out_path} は既に存在するためスキップ")
        return

    data["archived_at"] = datetime.now(timezone.utc).isoformat()
    data["git_commit"] = os.environ.get("GITHUB_SHA", "")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"{out_path} を保存しました")


if __name__ == "__main__":
    main()
