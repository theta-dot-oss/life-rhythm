#!/usr/bin/env python3
"""config.json と data/today.json の形式チェック。push 前と Pages のデプロイ時に実行する。"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
errors = []


def err(msg):
    errors.append(msg)


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(f"{path.name}: JSONとして読めない ({e})")
        return None


cfg = load(ROOT / "config.json")
if cfg is not None:
    for k in ("work_minutes", "break_minutes", "extend_minutes", "renotify_minutes", "renotify_max"):
        if not isinstance(cfg.get(k), (int, float)) or cfg[k] <= 0:
            err(f"config.json: {k} は正の数にする")
    for i, t in enumerate(cfg.get("timetable", [])):
        if not HHMM.match(str(t.get("time", ""))):
            err(f"config.json: timetable[{i}].time が HH:MM ではない: {t.get('time')}")
        if not t.get("label"):
            err(f"config.json: timetable[{i}].label がない")
    kinds = [t.get("kind") for t in cfg.get("timetable", [])]
    if "exercise" not in kinds:
        err("config.json: timetable に kind=exercise の行がない（運動の枠は固定）")
    ex = cfg.get("exercise", {})
    for d in map(str, range(7)):
        e = ex.get(d)
        if e is None:
            err(f"config.json: exercise[{d}] がない（0=日 … 6=土）")
            continue
        if not e.get("name"):
            err(f"config.json: exercise[{d}].name がない")
        for k in ("start", "end"):
            v = e.get(k)
            if v is not None and not HHMM.match(str(v)):
                err(f"config.json: exercise[{d}].{k} が HH:MM ではない: {v}")
    if not cfg.get("break_suggestions"):
        err("config.json: break_suggestions が空")

today = load(ROOT / "data" / "today.json")
if today is not None:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(today.get("date", ""))):
        err("today.json: date は YYYY-MM-DD")
    if not isinstance(today.get("tasks", []), list):
        err("today.json: tasks は配列")
    for i, e in enumerate(today.get("events", [])):
        for k in ("start", "end", "title"):
            if not e.get(k):
                err(f"today.json: events[{i}].{k} がない")
        if re.search(r"https?://|@", str(e.get("title", ""))):
            err(f"today.json: events[{i}].title にURLやメールアドレスが含まれている（ぼかす）")

if errors:
    print("\n".join("NG: " + e for e in errors))
    sys.exit(1)
print("OK: config.json / data/today.json")
