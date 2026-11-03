// Generates assets/cp-stats.svg from live Codeforces + LeetCode data.
// Node 18+ (uses built-in fetch). No dependencies.
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";

const CF_HANDLE = process.env.CF_HANDLE || "iamsiamhossen";
const LC_USER = process.env.LC_USER || "iamsiamhossen";
const OUT_SVG = "assets/cp-stats.svg";
const OUT_JSON = "assets/cp-stats.json"; // cache, used if an API is temporarily down

const UA = "Mozilla/5.0 (compatible; cp-stats-card/1.0)";

async function getJson(url, init = {}, tries = 3) {
  let err;
  for (let i = 0; i < tries; i++) {
    try {
      const res = await fetch(url, {
        ...init,
        headers: { "User-Agent": UA, ...(init.headers || {}) },
        signal: AbortSignal.timeout(20000),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      err = e;
      await new Promise((r) => setTimeout(r, 1500 * (i + 1)));
    }
  }
  throw err;
}

async function fetchCodeforces() {
  const base = "https://codeforces.com/api";
  const info = await getJson(`${base}/user.info?handles=${CF_HANDLE}`);
  if (info.status !== "OK") throw new Error(info.comment || "CF user.info failed");
  const u = info.result[0];

  const rating = await getJson(`${base}/user.rating?handle=${CF_HANDLE}`);
  const status = await getJson(`${base}/user.status?handle=${CF_HANDLE}&from=1&count=100000`);

  const subs = status.result || [];
  const solvedSet = new Set(
    subs
      .filter((s) => s.verdict === "OK")
      .map((s) => `${s.problem.contestId ?? s.problem.problemsetName}-${s.problem.index}`)
  );

  const okSubs = subs.filter((s) => s.verdict === "OK");
  const gymSolved = new Set(
    okSubs.filter((s) => (s.problem.contestId ?? 0) >= 100000).map((s) => `${s.problem.contestId}-${s.problem.index}`)
  ).size;
  console.log(
    `CF debug: ${subs.length} submissions, ${okSubs.length} OK verdicts, ${solvedSet.size} unique solved (gym: ${gymSolved})`
  );

  return {
    handle: CF_HANDLE,
    name: [u.firstName, u.lastName].filter(Boolean).join(" ") || CF_HANDLE,
    rank: u.rank || "unrated",
    rating: u.rating ?? null,
    maxRating: u.maxRating ?? null,
    contests: (rating.result || []).length,
    solved: solvedSet.size,
    submissions: subs.length,
    friends: u.friendOfCount ?? 0,
  };
}

async function fetchLeetCode() {
  const query = `
    query($u: String!) {
      allQuestionsCount { difficulty count }
      matchedUser(username: $u) {
        profile { ranking }
        submitStatsGlobal { acSubmissionNum { difficulty count } }
      }
    }`;
  const data = await getJson("https://leetcode.com/graphql", {
    method: "POST",
    headers: { "Content-Type": "application/json", Referer: "https://leetcode.com" },
    body: JSON.stringify({ query, variables: { u: LC_USER } }),
  });
  const d = data.data;
  if (!d?.matchedUser) throw new Error("LeetCode user not found");

  const pick = (arr, diff) => arr.find((x) => x.difficulty === diff)?.count ?? 0;
  const solved = d.matchedUser.submitStatsGlobal.acSubmissionNum;
  const total = d.allQuestionsCount;
  return {
    username: LC_USER,
    ranking: d.matchedUser.profile.ranking,
    solved: pick(solved, "All"),
    total: pick(total, "All"),
    easy: { s: pick(solved, "Easy"), t: pick(total, "Easy") },
    medium: { s: pick(solved, "Medium"), t: pick(total, "Medium") },
    hard: { s: pick(solved, "Hard"), t: pick(total, "Hard") },
  };
}

const esc = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const fmt = (n) => (n == null ? "—" : Number(n).toLocaleString("en-US"));

const RANK_COLORS = {
  unrated: "#8b949e",
  newbie: "#8b949e",
  pupil: "#3fb950",
  specialist: "#2fc7b8",
  expert: "#4f8dff",
  "candidate master": "#c26bff",
  master: "#f0a030",
  "international master": "#f0a030",
  grandmaster: "#f85149",
  "international grandmaster": "#f85149",
  "legendary grandmaster": "#f85149",
};
const titleCase = (s) => s.replace(/\b\w/g, (c) => c.toUpperCase());

function render({ cf, lc }) {
  const rankKey = String(cf.rank).toLowerCase();
  const rankColor = RANK_COLORS[rankKey] || "#8b949e";
  const rankText = titleCase(String(cf.rank));
  const pillW = Math.max(76, rankText.length * 8 + 28);
  const pillX = 398 - pillW;

  const R = 46;
  const C = 2 * Math.PI * R;
  const frac = lc.total ? lc.solved / lc.total : 0;
  const dash = Math.max(5, frac * C);

  const BAR_W = 232;
  const bar = (o, color, y) => {
    const w = Math.max(4, (o.t ? o.s / o.t : 0) * BAR_W);
    return `<rect x="600" y="${y}" width="${w.toFixed(1)}" height="6" rx="3" fill="${color}"/>`;
  };

  return `<svg xmlns="http://www.w3.org/2000/svg" width="860" height="260" viewBox="0 0 860 260" fill="none" role="img" aria-label="Competitive programming stats: Codeforces and LeetCode">
  <style>
    :root{--bg:#0d1117;--bg2:#121a24;--bd:#30363d;--tx:#e6edf3;--mu:#8b949e;--tr:#21262d;--ac:#3fb950}
    @media (prefers-color-scheme: light){:root{--bg:#ffffff;--bg2:#f6f8fa;--bd:#d0d7de;--tx:#1f2328;--mu:#656d76;--tr:#e6e9ed;--ac:#1a7f37}}
    text{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
    .lbl{font-size:11px;font-weight:600;letter-spacing:1.6px;fill:var(--mu)}
    .name{font-size:22px;font-weight:700;fill:var(--tx)}
    .big{font-size:44px;font-weight:800;fill:var(--tx)}
    .num{font-size:22px;font-weight:700;fill:var(--tx)}
    .sub{font-size:11px;font-weight:500;letter-spacing:.8px;fill:var(--mu)}
    .mu{font-size:13px;fill:var(--mu)}
    .row{font-size:13px;font-weight:600;fill:var(--tx)}
  </style>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" style="stop-color:var(--bg)"/>
      <stop offset="1" style="stop-color:var(--bg2)"/>
    </linearGradient>
    <linearGradient id="top" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" style="stop-color:var(--ac)" stop-opacity="0"/>
      <stop offset=".5" style="stop-color:var(--ac)"/>
      <stop offset="1" style="stop-color:var(--ac)" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect x=".5" y=".5" width="859" height="259" rx="14" fill="url(#bg)" style="stroke:var(--bd)"/>
  <rect x="40" y="0" width="780" height="2" fill="url(#top)"/>
  <line x1="430" y1="28" x2="430" y2="232" style="stroke:var(--bd)"/>

  <!-- CODEFORCES -->
  <g>
    <text x="32" y="44" class="lbl">CODEFORCES</text>
    <text x="32" y="74" class="name">${esc(cf.name)}</text>
    <rect x="${pillX}" y="28" width="${pillW}" height="26" rx="13" fill="${rankColor}" fill-opacity=".14" stroke="${rankColor}" stroke-opacity=".55"/>
    <text x="${pillX + pillW / 2}" y="45.5" text-anchor="middle" font-size="12" font-weight="700" fill="${rankColor}">${esc(rankText)}</text>

    <text x="32" y="130" class="big">${fmt(cf.rating)}</text>
    <text x="32" y="150" class="sub">CONTEST RATING</text>
    <text x="180" y="130" class="big" style="font-size:30px">${fmt(cf.maxRating)}</text>
    <text x="180" y="150" class="sub">MAX RATING</text>
    <text x="300" y="130" class="big" style="font-size:30px">${fmt(cf.contests)}</text>
    <text x="300" y="150" class="sub">CONTESTS</text>

    <line x1="32" y1="172" x2="398" y2="172" style="stroke:var(--bd)"/>

    <text x="32" y="205" class="num">${fmt(cf.solved)}</text>
    <text x="32" y="224" class="sub">SOLVED</text>
    <text x="150" y="205" class="num">${fmt(cf.submissions)}</text>
    <text x="150" y="224" class="sub">SUBMISSIONS</text>
    <text x="290" y="205" class="num">${fmt(cf.friends)}</text>
    <text x="290" y="224" class="sub">FRIENDS</text>
  </g>

  <!-- LEETCODE -->
  <g>
    <text x="462" y="44" class="lbl">LEETCODE</text>
    <text x="462" y="74" class="name">${esc(lc.username)}</text>
    <text x="828" y="44" text-anchor="end" class="mu">#${esc(lc.ranking)}</text>

    <circle cx="520" cy="158" r="${R}" stroke-width="9" style="stroke:var(--tr)"/>
    <circle cx="520" cy="158" r="${R}" stroke-width="9" stroke-linecap="round" stroke-dasharray="${dash.toFixed(2)} ${C.toFixed(2)}" transform="rotate(-90 520 158)" style="stroke:var(--ac)"/>
    <text x="520" y="166" text-anchor="middle" class="num" style="font-size:26px">${fmt(lc.solved)}</text>
    <text x="520" y="186" text-anchor="middle" class="sub" style="font-size:9px">SOLVED</text>

    <text x="600" y="116" class="row">Easy</text>
    <text x="832" y="116" text-anchor="end" class="mu">${fmt(lc.easy.s)} / ${fmt(lc.easy.t)}</text>
    <rect x="600" y="124" width="${BAR_W}" height="6" rx="3" style="fill:var(--tr)"/>
    ${bar(lc.easy, "#3fb950", 124)}

    <text x="600" y="158" class="row">Medium</text>
    <text x="832" y="158" text-anchor="end" class="mu">${fmt(lc.medium.s)} / ${fmt(lc.medium.t)}</text>
    <rect x="600" y="166" width="${BAR_W}" height="6" rx="3" style="fill:var(--tr)"/>
    ${bar(lc.medium, "#f0b429", 166)}

    <text x="600" y="200" class="row">Hard</text>
    <text x="832" y="200" text-anchor="end" class="mu">${fmt(lc.hard.s)} / ${fmt(lc.hard.t)}</text>
    <rect x="600" y="208" width="${BAR_W}" height="6" rx="3" style="fill:var(--tr)"/>
    ${bar(lc.hard, "#f85149", 208)}
  </g>
</svg>
`;
}

async function main() {
  const cache = existsSync(OUT_JSON) ? JSON.parse(readFileSync(OUT_JSON, "utf8")) : {};
  const out = { cf: cache.cf, lc: cache.lc };

  const [cf, lc] = await Promise.allSettled([fetchCodeforces(), fetchLeetCode()]);
  if (cf.status === "fulfilled") out.cf = cf.value;
  else console.warn("Codeforces fetch failed, using cache:", cf.reason?.message);
  if (lc.status === "fulfilled") out.lc = lc.value;
  else console.warn("LeetCode fetch failed, using cache:", lc.reason?.message);

  if (!out.cf || !out.lc) {
    console.error("Missing data and no cache available. Aborting.");
    process.exit(1);
  }

  mkdirSync("assets", { recursive: true });
  writeFileSync(OUT_JSON, JSON.stringify(out, null, 2) + "\n");
  writeFileSync(OUT_SVG, render(out));
  console.log("Updated", OUT_SVG);
}

main();
