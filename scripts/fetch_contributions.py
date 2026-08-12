from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Pedrssa"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")


def _parse_day(node):
    day = node.get("data-date")
    if not day:
        return None

    count_raw = node.get("data-count")
    count = int(count_raw) if count_raw and str(count_raw).isdigit() else 0

    level_raw = node.get("data-level", "0")
    try:
        level = max(0, min(4, int(level_raw)))
    except ValueError:
        level = 0

    return {"date": day, "count": count, "level": level}


def _streaks(days):
    active = sorted(date.fromisoformat(d["date"]) for d in days if d["count"] > 0)
    if not active:
        return 0, 0

    aset = set(active)
    longest = current_run = 1
    for prev, nxt in zip(active, active[1:]):
        if (nxt - prev).days == 1:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    cursor = date.today()
    if cursor not in aset:
        cursor -= timedelta(days=1)

    current = 0
    while cursor in aset:
        current += 1
        cursor -= timedelta(days=1)

    return current, longest


def main():
    headers = {
        "User-Agent": "Pedrssa-profile-readme/1.0 (+https://github.com/Pedrssa)",
        "Accept": "text/html,application/xhtml+xml",
    }
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    nodes = soup.select(
        "td.ContributionCalendar-day[data-date], rect.ContributionCalendar-day[data-date]"
    )
    days = [d for node in nodes if (d := _parse_day(node))]

    if not days:
        raise RuntimeError("No contribution cells found; GitHub markup may have changed.")

    current, longest = _streaks(days)
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])

    payload = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(days)} days")


if __name__ == "__main__":
    main()
