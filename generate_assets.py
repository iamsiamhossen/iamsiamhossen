"""
Generates the SVG assets used by README.md.

The contribution chart uses real data from the GitHub GraphQL API
(last 12 months of the account in GH_LOGIN). Run by the workflow in
.github/workflows/update-chart.yml, or locally:

    GH_TOKEN=<token> GH_LOGIN=iamsiamhossen python generate_assets.py

Without a token the chart is not overwritten, so wrong numbers are never shown.
Each asset is written in a dark and a light version.
"""
import json
import os
import urllib.request

LOGIN = os.environ.get("GH_LOGIN", "iamsiamhossen")
TOKEN = os.environ.get("GH_TOKEN", "")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
    }
  }
}
"""


def load_counts():
    """Return raw contribution counts, or None when no token is available."""
    if not TOKEN:
        return None
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json",
                 "User-Agent": "profile-readme-chart"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data or not data.get("data", {}).get("user"):
        raise SystemExit(f"GitHub API error: {data.get('errors', data)}")
    c = data["data"]["user"]["contributionsCollection"]
    return {
        "commits": c["totalCommitContributions"],
        "pull_requests": c["totalPullRequestContributions"],
        "issues": c["totalIssueContributions"],
        "code_review": c["totalPullRequestReviewContributions"],
    }

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

FONT = "-apple-system, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"

THEMES = {
    "dark": dict(text="#e6edf3", muted="#9da7b3", green="#3ddc5c",
                 line="#30363d", dot_core="#d9ffe0"),
    "light": dict(text="#1f2328", muted="#59636e", green="#1a9f3a",
                  line="#d0d7de", dot_core="#ffffff"),
}

GITHUB_PATH = (
    "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 "
    "0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7"
    "c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 "
    "3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 "
    "1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 "
    "1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 "
    "1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 "
    "2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
)


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)


def name_svg(t):
    # terminal icon + name only (subtitle and text are real HTML in README.md)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100" viewBox="0 0 400 100" role="img" aria-label="Siam Hossen">
  <g fill="none" stroke="{t['green']}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="4,6 17,17 4,28"/>
    <line x1="23" y1="30" x2="38" y2="30"/>
  </g>
  <text x="2" y="88" font-family="{FONT}" font-size="54" font-weight="700" fill="{t['text']}">Siam Hossen</text>
</svg>
"""


def accent(t):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="48" height="6" viewBox="0 0 48 6" role="presentation">
  <rect x="0" y="1" width="46" height="3.5" rx="1.75" fill="{t['green']}"/>
</svg>
"""


def link_email(t):
    g = t["green"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="96" height="34" viewBox="0 0 96 34" role="img" aria-label="Email">
  <g fill="none" stroke="{g}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="9" width="22" height="16" rx="3"/>
    <polyline points="4,11 14,19 24,11"/>
  </g>
  <text x="34" y="23.5" font-family="{FONT}" font-size="18" fill="{g}">Email</text>
</svg>
"""


def link_github(t):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="112" height="34" viewBox="0 0 112 34" role="img" aria-label="GitHub">
  <g transform="translate(2,5) scale(1.0)">
    <path d="{GITHUB_PATH}" fill="{t['muted']}"/>
  </g>
  <text x="34" y="23.5" font-family="{FONT}" font-size="18" fill="{t['green']}">GitHub</text>
</svg>
"""


def github_icon(t):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" role="img" aria-label="GitHub">
  <path d="{GITHUB_PATH}" fill="{t['text']}"/>
</svg>
"""


def composition(t, counts):
    g = t["green"]
    W, H = 340, 440
    cx, cy = 195, 220
    arms = {"left": 118, "right": 88, "top": 140, "bottom": 140}
    total = sum(counts.values())

    def share(key):
        if total == 0 or counts[key] == 0:
            return 0, ""
        p = counts[key] * 100 / total
        r = round(p)
        return p, ("<1%" if r == 0 else f"{r}%")

    sh = {k: share(k) for k in counts}
    seg = lambda key, arm: 0 if sh[key][0] == 0 else max(5, arm * sh[key][0] / 100)
    L = seg("commits", arms["left"])
    R = seg("issues", arms["right"])
    T = seg("code_review", arms["top"])
    B = seg("pull_requests", arms["bottom"])

    def glow(x2, y2):
        return (f'<line x1="{cx}" y1="{cy}" x2="{x2}" y2="{y2}" stroke="{g}" stroke-width="7" stroke-linecap="round" opacity="0.55" filter="url(#glow)"/>'
                f'<line x1="{cx}" y1="{cy}" x2="{x2}" y2="{y2}" stroke="{g}" stroke-width="3" stroke-linecap="round"/>'
                f'<circle cx="{x2}" cy="{y2}" r="7" fill="{g}"/><circle cx="{x2}" cy="{y2}" r="2.6" fill="{t["dot_core"]}"/>')

    segs = ""
    if L: segs += glow(cx - L, cy)
    if R: segs += glow(cx + R, cy)
    if T: segs += glow(cx, cy - T)
    if B: segs += glow(cx, cy + B)

    def pct_line(key, x, y, anchor):
        txt = sh[key][1]
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}">{txt}</text>' if txt else ""

    label = (f"Contribution composition, last 12 months: {counts['commits']} commits, "
             f"{counts['pull_requests']} pull requests, {counts['issues']} issues, "
             f"{counts['code_review']} code reviews")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
  <defs>
    <filter id="glow" x="-50%" y="-200%" width="200%" height="500%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <line x1="1" y1="12" x2="1" y2="{H-12}" stroke="{t['line']}" stroke-width="1"/>

  <g stroke="{g}" stroke-width="3" stroke-linecap="round" opacity="0.9">
    <line x1="{cx}" y1="{cy}" x2="{cx+arms['right']}" y2="{cy}"/>
    <line x1="{cx}" y1="{cy-arms['top']}" x2="{cx}" y2="{cy+arms['bottom']}"/>
    <line x1="{cx-arms['left']}" y1="{cy}" x2="{cx}" y2="{cy}"/>
  </g>

  {segs}

  <circle cx="{cx}" cy="{cy}" r="7.5" fill="{g}"/>
  <circle cx="{cx}" cy="{cy}" r="3.2" fill="{t['dot_core']}"/>

  <g font-family="{FONT}" font-size="16" fill="{t['text']}">
    {pct_line('code_review', cx, cy-arms['top']-40, 'middle')}
    <text x="{cx}" y="{cy-arms['top']-22}" text-anchor="middle">Code review</text>
    {pct_line('issues', cx+arms['right']+14, cy-6, 'start')}
    <text x="{cx+arms['right']+14}" y="{cy+16}" text-anchor="start">Issues</text>
    {pct_line('commits', cx-arms['left']-14, cy-6, 'end')}
    <text x="{cx-arms['left']-14}" y="{cy+16}" text-anchor="end">Commits</text>
    {pct_line('pull_requests', cx, cy+arms['bottom']+32, 'middle')}
    <text x="{cx}" y="{cy+arms['bottom']+54}" text-anchor="middle">Pull requests</text>
  </g>
</svg>
"""


for mode, t in THEMES.items():
    write(f"name.{mode}.svg", name_svg(t))
    write(f"accent.{mode}.svg", accent(t))
    write(f"email.{mode}.svg", link_email(t))
    write(f"github-link.{mode}.svg", link_github(t))
    write(f"github-icon.{mode}.svg", github_icon(t))

counts = load_counts()
if counts is None:
    print("No GH_TOKEN set: chart not updated (existing files kept).")
    for mode, t in THEMES.items():
        path = os.path.join(OUT, f"composition.{mode}.svg")
        if not os.path.exists(path):
            write(f"composition.{mode}.svg",
                  composition(t, {"commits": 0, "pull_requests": 0, "issues": 0, "code_review": 0}))
else:
    for mode, t in THEMES.items():
        write(f"composition.{mode}.svg", composition(t, counts))
    print("Chart updated from GitHub data:", counts)

print("Assets written to", OUT)
