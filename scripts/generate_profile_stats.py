#!/usr/bin/env python3
"""Generate reliable, self-hosted SVG stats for Talha Imran's GitHub profile."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

USER = "Talha-imran910"
API = "https://api.github.com"
OUT = Path("dist")
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def get_json(path: str):
    url = path if path.startswith("http") else API + path
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Talha-Imran-profile-stats",
    })
    if TOKEN:
        request.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def esc(value: object) -> str:
    text = str(value)
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


def card(title: str, rows: list[tuple[str, str]], width: int = 860, height: int = 250) -> str:
    y = 78
    lines = []
    for label, value in rows:
        lines.append(
            f'<text x="42" y="{y}" class="label">{esc(label)}</text>'
            f'<text x="810" y="{y}" text-anchor="end" class="value">{esc(value)}</text>'
        )
        y += 36
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/>
<text x="42" y="42" class="title">{esc(title)}</text>
<style>.title{{font:700 20px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#f0f6fc}}.label{{font:500 16px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#8b949e}}.value{{font:700 16px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#58a6ff}}</style>
{''.join(lines)}
</svg>'''


def language_card(counts: Counter[str], width: int = 860, height: int = 310) -> str:
    total = sum(counts.values()) or 1
    rows = []
    y = 78
    for language, count in counts.most_common(8):
        pct = count / total * 100
        rows.append(
            f'<text x="42" y="{y}" class="label">{esc(language)}</text>'
            f'<rect x="190" y="{y-15}" width="500" height="12" rx="6" fill="#21262d"/>'
            f'<rect x="190" y="{y-15}" width="{max(4, 500*pct/100):.1f}" height="12" rx="6" fill="#58a6ff"/>'
            f'<text x="810" y="{y}" text-anchor="end" class="value">{pct:.1f}%</text>'
        )
        y += 30
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/>
<text x="42" y="42" class="title">Talha Imran — Language Profile</text>
<style>.title{{font:700 20px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#f0f6fc}}.label{{font:500 14px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#8b949e}}.value{{font:700 14px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#58a6ff}}</style>
{''.join(rows)}
</svg>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    profile = get_json(f"/users/{USER}")
    repos = get_json(f"/users/{USER}/repos?per_page=100&type=owner&sort=updated")
    repos = [r for r in repos if not r.get("fork")]

    stars = sum(int(r.get("stargazers_count", 0)) for r in repos)
    forks = sum(int(r.get("forks_count", 0)) for r in repos)
    languages: Counter[str] = Counter()

    for repo in repos:
        try:
            data = get_json(repo["languages_url"])
            for language, amount in data.items():
                languages[language] += int(amount)
        except Exception:
            continue

    stats = card("Talha Imran — GitHub Signals", [
        ("Public repositories", profile.get("public_repos", len(repos))),
        ("Followers", profile.get("followers", 0)),
        ("Stars across owned repos", stars),
        ("Forks across owned repos", forks),
    ])
    (OUT / "profile-stats.svg").write_text(stats, encoding="utf-8")
    (OUT / "profile-languages.svg").write_text(language_card(languages), encoding="utf-8")


if __name__ == "__main__":
    main()
