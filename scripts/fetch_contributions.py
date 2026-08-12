from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Pedrssa"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")

COUNT_RE = re.compile(r"([\d,]+)\s+contributions?\b", re.IGNORECASE)


def _count_from_tooltip(soup: BeautifulSoup, node) -> int:
    node_id = node.get("id")
    if node_id:
        tip = soup.find("tool-tip", attrs={"for": node_id})
        if tip:
            text = tip.get_text(" ", strip=True)
            if text.lower().startswith("no contribution"):
                return 0
            match = COUNT_RE.search(text)
            if match:
                return int(match.group(1).replace(",", ""))

    count_raw = node.get("data-count")
    if count_raw and str(count_raw).isdigit():
        return int(count_raw)

    return 0


def _parse_day(soup: BeautifulSoup, node):
    day = node.get("data-date")
    if not day:
        return None

    count = _count_from_tooltip(soup, node)

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
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    nodes = soup.select("td.ContributionCalendar-day[data-date]")
    days = [d for node in nodes if (d := _parse_day(soup, node))]

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
    print(f"Wrote {OUT} with {len(days)} days and {total} contributions")


if __name__ == "__main__":
    main()
