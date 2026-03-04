#!/usr/bin/env python3
"""English Memory Work MVP

A lightweight local workflow for:
1) capturing new English expressions
2) planning spaced-review sessions
3) logging active recall practice
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List


DEFAULT_DB = Path("data/phrases.json")
DEFAULT_LOG = Path("data/review_log.jsonl")


@dataclass
class Phrase:
    id: int
    expression: str
    meaning_zh: str
    example_en: str
    source: str
    created_at: str
    next_review: str
    interval_days: int = 1
    ease: float = 2.5
    review_count: int = 0


def today() -> dt.date:
    return dt.date.today()


def load_db(path: Path) -> List[Phrase]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Phrase(**item) for item in data]


def save_db(path: Path, items: List[Phrase]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(item) for item in items], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def import_csv(db_path: Path, csv_path: Path) -> None:
    items = load_db(db_path)
    next_id = max((it.id for it in items), default=0) + 1
    imported = 0
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = Phrase(
                id=next_id,
                expression=row["expression"].strip(),
                meaning_zh=row.get("meaning_zh", "").strip(),
                example_en=row.get("example_en", "").strip(),
                source=row.get("source", "").strip(),
                created_at=today().isoformat(),
                next_review=today().isoformat(),
            )
            items.append(p)
            next_id += 1
            imported += 1
    save_db(db_path, items)
    print(f"Imported {imported} new items to {db_path}. Total: {len(items)}")


def due_items(db_path: Path) -> List[Phrase]:
    items = load_db(db_path)
    now = today()
    return [p for p in items if dt.date.fromisoformat(p.next_review) <= now]


def list_due(db_path: Path, limit: int) -> None:
    due = due_items(db_path)[:limit]
    if not due:
        print("No due items today. Great job!")
        return
    for p in due:
        print(f"[{p.id}] {p.expression} | 下次复习: {p.next_review} | 已复习: {p.review_count}")


def update_schedule(p: Phrase, quality: int) -> Phrase:
    quality = max(0, min(5, quality))
    if quality < 3:
        p.interval_days = 1
    else:
        if p.review_count == 0:
            p.interval_days = 1
        elif p.review_count == 1:
            p.interval_days = 3
        else:
            p.interval_days = max(1, round(p.interval_days * p.ease))
        p.ease = max(1.3, p.ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    p.review_count += 1
    p.next_review = (today() + dt.timedelta(days=p.interval_days)).isoformat()
    return p


def review_one(db_path: Path, log_path: Path, phrase_id: int, quality: int, recall_note: str) -> None:
    items = load_db(db_path)
    target = None
    for idx, p in enumerate(items):
        if p.id == phrase_id:
            target = (idx, p)
            break
    if target is None:
        raise ValueError(f"phrase_id={phrase_id} not found")

    idx, p = target
    p = update_schedule(p, quality)
    items[idx] = p
    save_db(db_path, items)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        event = {
            "at": dt.datetime.now().isoformat(timespec="seconds"),
            "phrase_id": phrase_id,
            "quality": quality,
            "next_review": p.next_review,
            "recall_note": recall_note,
        }
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(f"Updated phrase {phrase_id}, next review: {p.next_review}")


def prompt_quality() -> int:
    while True:
        raw = input("你的回忆质量（0-5，5最好）: ").strip()
        if raw.isdigit() and 0 <= int(raw) <= 5:
            return int(raw)
        print("请输入 0 到 5 的整数。")


def run_interactive_session(db_path: Path, log_path: Path, limit: int) -> None:
    due = due_items(db_path)[:limit]
    if not due:
        print("今天没有待复习条目，太棒了！")
        return

    print(f"今天待复习 {len(due)} 条，开始：\n")
    for idx, p in enumerate(due, start=1):
        print(f"--- [{idx}/{len(due)}] {p.expression} ---")
        input("先自己回忆含义和例句，回车后显示参考答案... ")
        print(f"参考含义: {p.meaning_zh}")
        print(f"参考例句: {p.example_en}")
        quality = prompt_quality()
        note = input("备注（可留空）: ").strip()
        review_one(db_path, log_path, p.id, quality, note)
        print()

    print("交互复习完成！你可以运行 due 查看剩余条目。")


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="English Memory Work CLI")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)

    sub = parser.add_subparsers(dest="command", required=True)

    p_import = sub.add_parser("import-csv", help="Import phrase CSV")
    p_import.add_argument("--csv", type=Path, required=True)

    p_due = sub.add_parser("due", help="Show due phrases")
    p_due.add_argument("--limit", type=int, default=20)

    p_review = sub.add_parser("review", help="Record one review result")
    p_review.add_argument("--phrase-id", type=int, required=True)
    p_review.add_argument("--quality", type=int, required=True, help="0-5 self-score")
    p_review.add_argument("--note", type=str, default="")

    p_session = sub.add_parser("session", help="Interactive review session for non-technical users")
    p_session.add_argument("--limit", type=int, default=20)

    return parser


def main() -> None:
    parser = init_parser()
    args = parser.parse_args()

    if args.command == "import-csv":
        import_csv(args.db, args.csv)
    elif args.command == "due":
        list_due(args.db, args.limit)
    elif args.command == "review":
        review_one(args.db, args.log, args.phrase_id, args.quality, args.note)
    elif args.command == "session":
        run_interactive_session(args.db, args.log, args.limit)


if __name__ == "__main__":
    main()
