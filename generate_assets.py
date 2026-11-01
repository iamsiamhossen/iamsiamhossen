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
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="126" viewBox="0 0 400 126" role="img" aria-label="Siam Hossen">
  <g fill="none" stroke="{t['green']}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="2,6 15,17 2,28"/>
    <line x1="21" y1="30" x2="36" y2="30"/>
  </g>
  <text x="0" y="100" font-family="{FONT}" font-size="54" font-weight="700" fill="{t['text']}">Siam Hossen</text>
</svg>
"""


def accent(t):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="48" height="16" viewBox="0 0 48 16" role="presentation">
  <rect x="0" y="8" width="46" height="3.5" rx="1.75" fill="{t['green']}"/>
</svg>
"""


LINKEDIN_PATH = ("M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046"
                 "c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 "
                 "2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 "
                 ".774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z")

LEETCODE_PATH = ("M13.483 0a1.374 1.374 0 0 0-.961.438L7.116 6.226l-3.854 4.126a5.266 5.266 0 0 0-1.209 2.104 5.35 5.35 0 0 0-.125.513 5.527 5.527 0 0 0 "
                 ".062 2.362 5.83 5.83 0 0 0 .349 1.017 5.938 5.938 0 0 0 1.271 1.818l4.277 4.193.039.038c2.248 2.165 5.852 2.133 8.063-.074l2.396-2.392"
                 "c.54-.54.54-1.414.003-1.955a1.378 1.378 0 0 0-1.951-.003l-2.396 2.392a3.021 3.021 0 0 1-4.205.038l-.02-.019-4.276-4.193c-.652-.64-.972-1.469"
                 "-.948-2.263a2.68 2.68 0 0 1 .066-.523 2.545 2.545 0 0 1 .619-1.164L9.13 8.114c1.058-1.134 3.204-1.27 4.43-.278l3.501 2.831c.593.48 1.461.387 "
                 "1.94-.207a1.384 1.384 0 0 0-.207-1.943l-3.5-2.831c-.8-.647-1.766-1.045-2.774-1.202l2.015-2.158A1.384 1.384 0 0 0 13.483 0zm-2.866 12.815a1.38 "
                 "1.38 0 0 0-1.38 1.382 1.38 1.38 0 0 0 1.38 1.382H20.79a1.38 1.38 0 0 0 1.38-1.382 1.38 1.38 0 0 0-1.38-1.382z")

PILL_H = 38


def pill(t, mode, label, icon, width):
    """Rounded button: brand-coloured icon + label."""
    fill = "#161b22" if mode == "dark" else "#f6f8fa"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{PILL_H}" viewBox="0 0 {width} {PILL_H}" role="img" aria-label="{label}">
  <rect x="0.5" y="0.5" width="{width-1}" height="{PILL_H-1}" rx="{PILL_H/2-0.5}" fill="{fill}" stroke="{t['line']}"/>
  <g transform="translate(15,10) scale(0.75)">{icon}</g>
  <text x="41" y="24.5" font-family="{FONT}" font-size="15" font-weight="500" fill="{t['text']}">{label}</text>
</svg>
"""


def pill_icons(t, mode):
    dark = mode == "dark"
    green = t["green"]
    return {
        "email": ("Email", f'<g fill="none" stroke="{green}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                           f'<rect x="2" y="5" width="20" height="14" rx="3"/><polyline points="3,7.5 12,14 21,7.5"/></g>'),
        "github": ("GitHub", f'<path d="{GITHUB_PATH}" fill="{t["text"]}"/>'),
        "linkedin": ("LinkedIn", f'<path d="{LINKEDIN_PATH}" fill="{"#3b8de0" if dark else "#0a66c2"}"/>'),
        "codeforces": ("Codeforces",
                       f'<rect x="0" y="7.5" width="6" height="13.5" rx="1.5" fill="#f5b921"/>'
                       f'<rect x="9" y="3" width="6" height="18" rx="1.5" fill="#2f95d6"/>'
                       f'<rect x="18" y="10.5" width="6" height="10.5" rx="1.5" fill="{"#f0525c" if dark else "#d32f3f"}"/>'),
        "leetcode": ("LeetCode", f'<path d="{LEETCODE_PATH}" fill="#ffa116"/>'),
    }


def pill_width(label):
    return round(41 + len(label) * 8.0 + 17)


def github_icon(t):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" role="img" aria-label="GitHub">
  <path d="{GITHUB_PATH}" fill="{t['text']}"/>
</svg>
"""


def composition(t, counts):
    g = t["green"]
    W, H = 390, 540
    cx, cy = 218, 268
    arms = {"left": 112, "right": 84, "top": 170, "bottom": 170}
    total = sum(counts.values())

    def share(key):
        if total == 0 or counts[key] == 0:
            return 0, ""
        p = counts[key] * 100 / total
        r = round(p)
        return p, ("&lt;1%" if r == 0 else f"{r}%")

    sh = {k: share(k) for k in counts}
    seg = lambda key, arm: 0 if sh[key][0] == 0 else max(5, arm * sh[key][0] / 100)
    L = seg("commits", arms["left"])
    R = seg("issues", arms["right"])
    T = seg("code_review", arms["top"])
    B = seg("pull_requests", arms["bottom"])

    def glow(x2, y2):
        return (f'<line x1="{cx}" y1="{cy}" x2="{x2}" y2="{y2}" stroke="{g}" stroke-width="11" stroke-linecap="round" opacity="0.5" filter="url(#glow)"/>'
                f'<line x1="{cx}" y1="{cy}" x2="{x2}" y2="{y2}" stroke="{g}" stroke-width="4.5" stroke-linecap="round"/>'
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
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <line x1="1" y1="12" x2="1" y2="{H-12}" stroke="{t['line']}" stroke-width="1"/>

  <g stroke="{g}" stroke-width="3" stroke-linecap="round" stroke-opacity="0.9">
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
    for key, (label, icon) in pill_icons(t, mode).items():
        write(f"pill-{key}.{mode}.svg", pill(t, mode, label, icon, pill_width(label)))
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
