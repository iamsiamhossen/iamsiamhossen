import json
import math
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]

now = datetime.now(timezone.utc)
start = now - timedelta(days=365)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
    }
  }
}
"""

payload = {
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": start.isoformat(),
        "to": now.isoformat()
    }
}

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "GitHub-Profile-Activity"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

if result.get("errors"):
    raise RuntimeError(result["errors"])

user = result["data"]["user"]
if user is None:
    raise RuntimeError(f"GitHub user not found: {USERNAME}")

data = user["contributionsCollection"]

stats = {
    "commits": data["totalCommitContributions"],
    "issues": data["totalIssueContributions"],
    "reviews": data["totalPullRequestReviewContributions"],
    "pull_requests": data["totalPullRequestContributions"]
}

maximum = max(stats.values(), default=0)

def arm_length(value):
    if maximum == 0:
        return 90
    return 45 + 115 * math.sqrt(value / maximum)

left = arm_length(stats["commits"])
right = arm_length(stats["issues"])
top = arm_length(stats["reviews"])
bottom = arm_length(stats["pull_requests"])

svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="500" height="520" viewBox="0 0 500 520">
  <rect width="500" height="520" fill="#0d1117"/>

  <line x1="2" y1="2" x2="2" y2="518"
        stroke="#30363d" stroke-width="2"/>

  <g stroke="#2fce60" stroke-width="3" stroke-linecap="round">
    <line x1="250" y1="260" x2="{250-left:.1f}" y2="260"/>
    <line x1="250" y1="260" x2="{250+right:.1f}" y2="260"/>
    <line x1="250" y1="260" x2="250" y2="{260-top:.1f}"/>
    <line x1="250" y1="260" x2="250" y2="{260+bottom:.1f}"/>
  </g>

  <circle cx="250" cy="260" r="8" fill="#2fce60"/>
  <circle cx="250" cy="260" r="3.5" fill="#d0f5da"/>

  <g fill="#e6edf3" font-family="Arial, sans-serif" font-size="16">
    <text x="250" y="45" text-anchor="middle">Code review</text>
    <text x="250" y="68" text-anchor="middle" font-size="12" fill="#8b949e">{stats["reviews"]}</text>

    <text x="30" y="255">Commits</text>
    <text x="30" y="278" font-size="12" fill="#8b949e">{stats["commits"]}</text>

    <text x="425" y="255">Issues</text>
    <text x="425" y="278" font-size="12" fill="#8b949e">{stats["issues"]}</text>

    <text x="250" y="475" text-anchor="middle">Pull requests</text>
    <text x="250" y="498" text-anchor="middle" font-size="12" fill="#8b949e">{stats["pull_requests"]}</text>
  </g>
</svg>
"""

output = Path("assets/activity-cross.svg")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(svg, encoding="utf-8")

print("Generated activity graph:", stats)
