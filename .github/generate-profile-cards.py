import json
import os
import urllib.request
from collections import Counter

USER = "NgocTien0110"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github+json"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def get(path):
    request = urllib.request.Request(
        f"https://api.github.com{path}", headers=HEADERS
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def card(width, height, title, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>text {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }} .title {{ fill:#e6edf3;font-size:20px;font-weight:600 }} .label {{ fill:#8b949e;font-size:13px }} .value {{ fill:#58a6ff;font-size:22px;font-weight:600 }}</style>
<rect width="100%" height="100%" rx="8" fill="#0d1117" stroke="#30363d"/>
{body}
</svg>
"""


user = get(f"/users/{USER}")
repos = get(f"/users/{USER}/repos?per_page=100&sort=updated")
languages = Counter()
for repo in repos:
    if not repo.get("fork"):
        try:
            for language, amount in get(repo["languages_url"]).items():
                languages[language] += amount
        except urllib.error.HTTPError:
            pass

total_bytes = sum(languages.values()) or 1
top_languages = languages.most_common(5)

stats_body = f"""<text x="24" y="36" class="title">{esc(USER)}'s GitHub Stats</text>
<text x="24" y="76" class="label">Public repositories</text><text x="250" y="78" class="value">{user.get("public_repos", 0)}</text>
<text x="24" y="116" class="label">Followers</text><text x="250" y="118" class="value">{user.get("followers", 0)}</text>
<text x="24" y="156" class="label">Following</text><text x="250" y="158" class="value">{user.get("following", 0)}</text>
<text x="24" y="196" class="label">Total stars</text><text x="250" y="198" class="value">{sum(r.get("stargazers_count", 0) for r in repos)}</text>"""

langs_body = f"""<text x="24" y="36" class="title">Most Used Languages</text>"""
for index, (language, amount) in enumerate(top_languages):
    y = 76 + index * 34
    percentage = amount * 100 / total_bytes
    langs_body += f"""<text x="24" y="{y}" class="label">{esc(language)}</text>
<rect x="130" y="{y-12}" width="170" height="10" rx="5" fill="#21262d"/>
<rect x="130" y="{y-12}" width="{max(3, 170 * percentage / 100):.1f}" height="10" rx="5" fill="#58a6ff"/>
<text x="316" y="{y}" class="label">{percentage:.1f}%</text>"""

trophy_body = f"""<text x="24" y="36" class="title">GitHub Profile Trophy</text>
<text x="45" y="92" font-size="38">🏆</text><text x="98" y="82" class="label">Repositories</text><text x="98" y="108" class="value">{user.get("public_repos", 0)}</text>
<text x="230" y="92" font-size="38">⭐</text><text x="283" y="82" class="label">Stars</text><text x="283" y="108" class="value">{sum(r.get("stargazers_count", 0) for r in repos)}</text>
<text x="410" y="92" font-size="38">👥</text><text x="463" y="82" class="label">Followers</text><text x="463" y="108" class="value">{user.get("followers", 0)}</text>"""

os.makedirs("dist", exist_ok=True)
open("dist/profile-stats.svg", "w").write(card(420, 220, "stats", stats_body))
open("dist/top-langs.svg", "w").write(card(420, 220, "languages", langs_body))
open("dist/profile-trophy.svg", "w").write(card(650, 140, "trophy", trophy_body))
