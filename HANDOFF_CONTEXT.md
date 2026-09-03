# REAP Deal Screener — Handoff Context

This is a Claude skill (`reap-deal-underwriter/`) built for Owen, a student in Marquette
University's Real Estate Asset Program (REAP). It was developed iteratively in a chat session;
this doc summarizes what it does, why it's shaped the way it is, and what's worth building next
in Claude Code — particularly the areas that need real engineering rather than prompt/instruction
tuning.

## What this actually is

REAP's real process: Vito (presumably faculty/advisor) presents a deal in class with a SWOT
(Strengths/Weaknesses/Opportunities/Threats) and an "Unknowns" list on the board. Each analyst
then has **48 hours** to form an opinion — **Pursue or Pass** — before the class decides by
majority vote.

This skill exists to help a student get from "here's an OM Vito handed out" to "here's my
SWOT + Unknowns + Pursue/Pass call" fast, in the same format that's already on the board — not to
produce a generic real-estate memo.

Two important framing decisions, both non-negotiable given how the skill evolved:

1. **REAP invests as a limited, non-controlling equity partner (an LP), not a GP.** Every
   recommendation has to be based on REAP's actual post-promote, investor-level return — not
   the project-level IRR/multiple the sponsor's offering memorandum headlines. Figuring out
   which share class REAP would realistically enter (by check size) and running the waterfall
   math to get REAP's real number is the analytical core of the whole skill.
2. **REAP has no formal buy-box.** There's no house IRR hurdle, no minimum equity multiple policy
   — the group hasn't set one. The skill uses general institutional CRE-LP reference ranges as
   context for judgment, and says so explicitly in every output, rather than pretending REAP has
   house criteria it doesn't have.

## How the skill evolved (context for why it's shaped this way)

It started as a **full underwriting model generator** — build a 5-6 tab Excel model + a one-page
memo for every deal Vito sends, deliberately with no verdict (the idea being "every deal gets the
reps, this is a teaching tool, not a screener"). That's still in there as an optional secondary
step (`assets/model_template_notes.md` + `references/memo-format.md`), but it is **no longer the
default output**.

Owen redirected it hard: the actual goal isn't to underwrite every deal in detail — it's to help
him reach a **fast, defensible opinion** for the 48-hour vote. So the primary deliverable is now
a short "screener" document (`references/screener-format.md`) that mirrors the board format
(SWOT + Unknowns, verdict-first), and the full model only gets built later, for a deal the class
actually votes to pursue.

## File map

- `SKILL.md` — the workflow (10 steps) and top-level framing. Read this first.
- `references/screener-format.md` — the primary deliverable's format. Verdict-led, symbol-coded,
  scannable — designed to be read on a phone in a couple minutes.
- `references/screening-benchmarks.md` — general institutional LP reference ranges (IRR, equity
  multiple, DSCR, leverage, basis) used as context, explicitly *not* presented as REAP policy.
  Also where the exit-cap web-search verification logic lives in detail (see below).
- `references/claim-verification.md` — the generalized version of that pattern: nine categories
  of OM claims worth verifying against live public sources (financing rate, yield/cap rate,
  growth assumptions, cited comps, location claims, environmental risk, entitlement status,
  supply pipeline, sponsor background), applicable to any asset type. Which categories apply to a
  given deal is a per-deal judgment call, not a fixed checklist.
- `references/input-schema.md` — what fields to pull from a deal, tagged `[SCREEN]` vs.
  `[DEEP-DIVE]` so the fast path doesn't accidentally turn into a full underwrite by habit.
- `references/asset-defaults.md` — fallback assumptions when the OM doesn't state something,
  always flagged rather than silently assumed.
- `references/deal-log-format.md` — a running `deal_log.csv` record (verdict, LP-level return,
  vote deadline, and — once known — how the class actually voted, so hit-rate can be tracked
  over a semester). Logged in the background; not delivered as a file unless asked.
- `references/mcp-integration.md` — how to reach REAP OS (a deal-inbox system Owen's account has
  some connector for) from either a direct-tool surface (e.g. Claude Code) or an
  artifact/API-only surface (claude.ai chat). **This is speculative** — written defensively based
  on how the connector showed up in the environment, never actually tested against a live REAP OS
  endpoint. Real priority for Claude Code: wire this up for real and test it, once Owen confirms
  there's something in the REAP OS inbox to pull.
- `assets/model_template_notes.md` — the full 5-6 tab Excel underwriting model structure
  (Deal Summary, Assumptions, Pro Forma, Debt Schedule, Returns, optional Sensitivity), now
  secondary/optional — only built post-vote for a pursued deal.
- `references/memo-format.md` — the optional deeper-dive memo that can accompany the full model.

## The claim-verification feature (Owen's idea, generalized across asset types)

Early screens were checking the OM's exit cap / going-in yield assumption only against generic
institutional benchmarks — which meant a sponsor's optimistic cap rate assumption could sail
through unchallenged. Owen's fix, generalized: **any specific, checkable claim an OM makes gets
verified against a live public source instead of accepted at face value** — not just the cap
rate, and not tied to any specific asset type or the two example deals (Juniper Apartments,
Sonne Residences) this skill was developed against.

This lives in two places now:

- `references/screening-benchmarks.md` — the exit cap check specifically, in detail. This one
  always runs, on every deal, because terminal value usually drives most of the return case.
- `references/claim-verification.md` — the general framework. Nine claim **categories** that show
  up in nearly any OM regardless of asset type (financing rate/index, yield/cap rate, growth
  assumptions, cited comps, location/market claims, physical/environmental risk, entitlement/deal
  status, supply pipeline, sponsor background), each mapped to what kind of public source would
  verify it. Which categories actually apply to a given deal — and how deep to go on each — is a
  judgment call based on what's actually present and material in that specific OM, not a fixed
  checklist run mechanically every time. The category framework is universal; the specific check
  (which index, which public database, which named comp) adapts to whatever asset type and deal
  structure is actually in front of the analyst.

Current cap-rate-specific logic (documented in detail in `screening-benchmarks.md`):

1. Search for the deal's actual named market first (many brokerages — Marcus & Millichap
   especially — publish dedicated reports for 40-50+ individual metros, not just the top 15-20).
2. Don't gatekeep to big-name brokerages (CBRE/JLL/M&M/C&W) — any reliable, named, tiered source
   works (regional brokerages, county/city economic development reports, RealPage, Yardi Matrix,
   CoStar-sourced coverage, credible local business-journal reporting citing licensed data).
3. What matters is the **tier breakout** (market *and* asset-class/quality tier — e.g. "suburban
   Class A"), not a blended national headline number, which will make a small or boutique deal
   look more mispriced than it is.
4. If a report exists but its actual cap rate figure is in a chart/graphic rather than
   extractable text, say so explicitly rather than blending a proxy number in as if it were
   precise — this came up for real on a Milwaukee deal, where Marcus & Millichap clearly
   publishes a dedicated Milwaukee report, but its chart values weren't retrievable via a plain
   web fetch.
5. Only fall back to a comparable market as an explicit, labeled proxy if a genuine search for
   the actual market turns up nothing usable.
6. Adjust for scale — a small boutique asset (e.g. 14 units) typically trades at a premium
   (higher cap rate, lower value) to the institutional-scale range most surveys are built from;
   note that explicitly rather than applying an institutional-scale number directly.

**This whole pattern — not just the cap rate instance of it — is the single highest-value thing
to harden in Claude Code**, for a concrete reason: right now every category in
`claim-verification.md` depends on whatever a generic web_search tool's snippets happen to
surface, and (confirmed for real on the cap rate check) reports often have their actual numbers
embedded in chart images that a text-based fetch can't read. In a coding environment each
category becomes a genuinely solvable, scriptable problem rather than a hopeful search:

- Programmatic PDF fetch + chart/image extraction (e.g. `pdfplumber`/`PyMuPDF` to pull embedded
  images, then a vision-capable call to read the chart values) instead of hoping search snippets
  contain the number in prose — useful for cap rate surveys specifically, but the same technique
  applies to any claim-verification category where the source data is graphical (rent trend
  charts, vacancy trend charts, supply pipeline charts).
- A small local cache/lookup of recently-verified figures by category + market + asset tier
  (cap rates, rent growth indices, whatever else gets checked), built up over the semester as more
  deals get screened, so repeat markets (Milwaukee will come up again) don't need a fresh
  from-scratch search every time — this generalizes across every category in
  `claim-verification.md`, not just cap rate.
- API integrations per claim category, for the ones that have a real free/public API rather than
  requiring search-and-scrape: FRED for Treasury/SOFR rates (category 1), Census/BLS for
  population and employment claims (category 5), FEMA for flood zone data (category 6), and — if
  ever available — a paid CRE data source (CoStar, Yardi Matrix, RealPage, Real Capital Analytics)
  for cap rates and comps (categories 2 and 4), which would be a categorical upgrade over public
  web search for those specifically.
- A basic sponsor-background search routine (category 9) — currently the skill does this for
  zero deals; even a simple "search the sponsor entity name + principal names for news/litigation"
  step would be new coverage, not a hardening of something that already exists.

## Other things worth doing in Claude Code specifically (vs. staying in chat)

- **Actually wire up and test the REAP OS connector** (see `mcp-integration.md`) once there's a
  real deal in the inbox to pull — this needs a real dev loop (auth, endpoint testing, error
  handling), not a markdown description of intended behavior.
- **Git-track the skill** so changes across the semester (and any other REAP officers who touch
  it) have real history/diffs, instead of relying on conversational edit history.
- Everything else — running an actual screen on a new deal, writing the SWOT, computing LP-level
  returns, building the optional full model — works fine in chat with this skill as-is and
  doesn't need a coding environment. Don't rebuild what isn't broken; extend what's listed above.

## Known rough edges / open questions to be aware of

- `mcp-integration.md` is unvalidated — treat it as a best-guess design, not confirmed-working
  code.
- The debt schedule in the optional full model (`assets/model_template_notes.md`) uses a monthly
  amortization roll-up specifically to avoid an earlier bug where an annual-only `PMT` calc
  couldn't handle non-whole-year interest-only periods — worth keeping if this gets reimplemented
  in code rather than an Excel formula chain.
- `screening-benchmarks.md`'s numeric ranges (IRR, equity multiple, DSCR, etc.) are explicitly
  *not* REAP policy — starter/general context only. If REAP ever adopts real criteria, that file
  is where they'd go, replacing the "no formal buy-box" framing.

## Verification scripts: live-tested (2026-09-03)

All 7 scripts in `.claude/skills/reap-deal-underwriter/scripts/` were built with fixture-based
unit tests only (this session's sandbox blocks live network calls), then live-tested afterward
against real APIs and real sources from Owen's own machine. All 7 are now confirmed working
end-to-end: `fred_rate.py` (FRED), `census_lookup.py` (Census ACS + BLS LAUS), `fema_flood_check.py`
(Census Geocoder + FEMA NFHL), `verified_data_cache.py` (local, no network), `cap_rate_search.py`
(pulled Milwaukee's real multifamily cap rate ranges out of a 34-page CBRE PDF survey),
`pdf_chart_extract.py` (extracted embedded chart images from the same PDF), and
`sponsor_background_check.py` (confirmed both a clean-negative and a real true-positive litigation
hit). Three real bugs were found and fixed in the process: FEMA's REST host path had moved
(`/gis/nfhl/rest/...` → `/arcgis/rest/...`), and `cap_rate_search.py` needed two rounds of fixes to
stop flooding the caller with near-duplicate/mislabeled candidates from dense rate-survey tables.
Nothing here is speculative anymore — treat the scripts as working, not just unit-tested.

**Cross-market/cross-asset-class check (same day):** re-ran the location-lookup and cap-rate
scripts against Dallas, TX industrial — a market and asset class neither the scripts nor their
tests were built around — with zero code changes. `census_lookup.py` correctly pulled Dallas
city's actual population decline (-1.46%, 2018→2023 ACS); `fema_flood_check.py` geocoded a Dallas
address and returned its real flood zone; `cap_rate_search.py --market Dallas --asset-tier
industrial` against the same CBRE Cap Rate Survey PDF used for Milwaukee correctly ranked the
Dallas/Ft. Worth Industrial Class A row (3.25%-4.25% H2 2021) above four other asset-type tables
(apartment, office, retail, hotel) for the same market in that document. Confirms the scripts
generalize to any location/asset type without modification, as designed.
