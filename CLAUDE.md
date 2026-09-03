# REAP Deal Screener — Implementation Brief for Claude Code

You're picking up engineering work on `reap-deal-underwriter`, a Claude skill built for Owen, a
student in Marquette's Real Estate Asset Program (REAP). Read `HANDOFF_CONTEXT.md` first for the
full narrative — this file is the actionable task list that follows from it.

## What you're building, in one sentence
Turn the skill's claim-verification logic — currently just instructions telling Claude to
"go web-search this" — into real scripts that fetch from actual public data sources, so every
deal gets more precise, more consistently-sourced numbers instead of whatever a web search
snippet happens to surface.

## Architecture: skill scripts, not a separate app
This skill runs inside Claude's chat environment, which has a sandboxed computer with
`bash_tool` (run shell/Python), `web_search`, and file read/write. Other built-in skills in that
environment (docx, pptx, xlsx) ship a `scripts/` folder with small, single-purpose Python scripts
that get invoked via `bash_tool` mid-task — e.g. the xlsx skill's `scripts/recalc.py`. **Follow
that same pattern here.** Don't build a standalone service or webapp; build small scripts that:

1. Take clear CLI args (deal location, asset type, claim category, etc.)
2. Hit a real public API or a well-defined scrape target
3. Print structured output (JSON is fine) with the figure, the source, and the as-of date
4. Fail loudly and specifically when they can't find something — never silently return nothing

Then update the relevant `references/*.md` file to say "run `scripts/<name>.py` with these args"
instead of "search the web for X." The scripts are the implementation; the markdown files are
still the source of truth for *when* and *why* to use them — keep both in sync.

Repo layout to create:
```
reap-deal-underwriter/
  SKILL.md                          (existing — update to reference scripts where relevant)
  references/                       (existing)
  assets/                           (existing)
  scripts/                          (new — this is what you're building)
    fred_rate.py
    census_lookup.py
    fema_flood_check.py
    cap_rate_search.py
    pdf_chart_extract.py
    verified_data_cache.py
    sponsor_background_check.py
  tests/                            (new)
    fixtures/                       (sample OM excerpts / known-good answers for regression tests)
    test_fred_rate.py
    ...
```

## Priority-ordered task backlog

Work top to bottom. Each task lists the target file, the data source, and what "done" looks like.
Test every script against **both known deals** as regression cases before considering it done:
- **Juniper Apartments** — 169-unit stabilized multifamily acquisition, Fitchburg (Madison), WI.
  Exit cap in the OM: 5.50%.
- **Sonne Residences** — 14-unit ground-up "Missing Middle" development, Wauwatosa (Milwaukee),
  WI. Exit cap in the OM: 5.25%.
Both are real OMs already run through the skill manually — you have a known-good manual answer
to check each script's output against.

### 1. `scripts/fred_rate.py` — financing rate/index verification (claim-verification.md category 1)
**Why first:** cleanest free API, no auth required for basic series, immediately useful.
- Source: FRED (Federal Reserve Economic Data) API — `https://fred.stlouisfed.org/docs/api/fred/`.
  Free API key, instant signup. Relevant series: `DGS7` (7-Year Treasury), `DGS10` (10-Year
  Treasury), `SOFR` (Secured Overnight Financing Rate).
- CLI: `python fred_rate.py --series DGS7` → prints the latest value, its date, and the source URL.
- Done when: running it for the series used in Juniper's OM ("7-Year Treasury + 140 bps") returns
  a dated, sourced number Claude can add the spread to directly, replacing the manual web-search
  step that was previously needed for this exact check.

### 2. `scripts/census_lookup.py` — location/market claims (category 5)
- Source: U.S. Census Bureau API (`https://www.census.gov/data/developers/data-sets.html`) —
  free, key optional for low volume. Use the American Community Survey (ACS) for population,
  median household income, employment by industry, at the metro or county level.
- Also wire up BLS (Bureau of Labor Statistics) API for local unemployment rate —
  `https://www.bls.gov/developers/` — free, registered key.
- CLI: `python census_lookup.py --geo "Wauwatosa, WI" --metric population_growth` (and similar for
  median_income, employment_by_sector, unemployment_rate).
- Done when: it can verify or contradict a specific narrative claim (e.g. Sonne's OM claim about
  Wauwatosa Village median household income, or Juniper's claims about Fitchburg/Madison
  population growth and unemployment) with a cited, dated figure.

### 3. `scripts/fema_flood_check.py` — physical/environmental risk (category 6)
- Source: FEMA National Flood Hazard Layer — `https://www.fema.gov/flood-maps/national-flood-hazard-layer`,
  has a public REST API/data service. Input an address or lat/long, get flood zone designation.
- CLI: `python fema_flood_check.py --address "7746 Menomonee River Parkway, Wauwatosa, WI"`.
- Done when: it returns a flood zone designation for both known deals (Sonne is literally on a
  river parkway — good real test case) with source/date.

### 4. `scripts/cap_rate_search.py` — the cap rate check (screening-benchmarks.md, highest priority category)
**This is the one that's already been through the most manual iteration — read
`references/screening-benchmarks.md`'s "Cap rate is location-specific" section closely before
touching this.**
- No single clean free API exists for this one — it's inherently a search-and-extract problem,
  which is why it's separate from the API-based scripts above.
- Build it as: (a) targeted web search for the deal's named market + asset type, preferring named
  tiered sources over blended national headlines (CBRE, JLL, Marcus & Millichap, Cushman &
  Wakefield, but explicitly not gatekept to only those four — see `claim-verification.md`); (b) if
  a promising PDF report is found, fetch it and check both extractable text *and* embedded
  images/charts (this is where `pdf_chart_extract.py`, task 5, plugs in); (c) structured output:
  figure, range, tier, source, date, and — critically — whether the number came from text or from
  a chart image, so the caller can represent confidence accurately.
- Done when: run against Sonne (Wauwatosa/Milwaukee) it either finds Marcus & Millichap's
  Milwaukee-specific figure for real (stretch goal — depends on task 5) or clearly reports "found
  the report, its chart wasn't extractable, here's the best quantified proxy with citation"
  exactly like the manual process already did — script output should not be *worse* than the
  manual result, only faster/more consistent.

### 5. `scripts/pdf_chart_extract.py` — the actual unblock for #4
**This is the single highest-value script in this whole backlog.** The concrete problem: Marcus &
Millichap publishes a dedicated Milwaukee multifamily report with real cap rate data, but the
figure lives in a chart graphic, not in extractable PDF text — confirmed by hand during manual
screening.
- Approach: fetch the PDF, use `pdfplumber` or `PyMuPDF` (`fitz`) to extract embedded images from
  relevant pages, then pass each image to a vision-capable model call to read the chart's axis
  labels and data point values. Return structured output (chart title, axis labels, extracted
  value(s), confidence).
- Test fixture: use the Marcus & Millichap 2025 National Multifamily Investment Forecast PDF
  (publicly available — was located during manual screening at
  `bagliericommercial.com/wp-content/uploads/2025/06/2025-Multifamily-Investment-Forecast.pdf`,
  though the live URL should be re-verified) as a known test case containing per-market cap rate
  charts, including one for Milwaukee.
- Done when: it can extract a specific numeric cap rate value for at least one market from that
  report's chart, that a human can verify against the chart image directly.

### 6. `scripts/verified_data_cache.py` — cross-deal caching layer
- Purpose: once a market + asset-class tier + category has been verified for one deal, don't
  re-search from scratch for the next deal in the same market (Milwaukee will come up again).
- Simple approach is fine: a local JSON or SQLite store keyed by (category, market, asset_tier),
  storing the verified figure, source, and as-of date, with a sensible staleness cutoff (e.g.
  re-verify if the cached entry is more than ~90 days old, since cap rate surveys update
  biannually/quarterly).
- Done when: running `cap_rate_search.py` twice for the same market in quick succession is
  visibly faster/cheaper the second time, and the skill's screener output can note "cached from
  [date]" when it uses a cached figure.

### 7. `scripts/sponsor_background_check.py` — category 9, currently zero coverage
- Purpose: basic news/litigation search on a named sponsor entity + principals — the skill
  currently does none of this, so this is net-new coverage, not hardening.
- Approach: targeted web search for "[sponsor entity name]" + "[principal name]" combined with
  terms like "lawsuit," "litigation," "SEC," "complaint," "bankruptcy" — summarize findings,
  clearly distinguish "nothing found" (worth noting as a limitation, not a clean bill of health)
  from "found and here's what."
- Done when: run against JJH3group/Jeffrey Hook (Sonne's sponsor) and Wangard Partners (Juniper's
  sponsor) it produces a short, cited summary either way.

### 8. REAP OS MCP connector — do this last, and only once there's a live deal to test against
See `references/mcp-integration.md` — it's written defensively/speculatively based on how the
connector surfaced in the chat environment, never tested against a real endpoint. Don't build
against a guess; wait until Owen confirms there's something in the REAP OS inbox, then build and
test the actual connection (auth flow, endpoint shape, error handling) for real.

## After each script works: close the loop back into the skill
For each completed script, update the relevant `references/*.md` file so the *instructions*
Claude follows during a normal screening session point at the script instead of describing a
generic web search. Example: once `fred_rate.py` works, `claim-verification.md`'s category 1
entry should say "run `scripts/fred_rate.py --series <X>`" rather than "verify the index's actual
current value from a primary source." The scripts only make the skill better if the markdown
instructions actually invoke them — a working script nobody calls is dead code.

## Non-goals — don't relitigate these, they're settled product decisions
- The screener format (`references/screener-format.md`) — SWOT + Unknowns, verdict-first, binary
  Pursue/Pass. This mirrors REAP's actual classroom board format. Don't redesign it.
- REAP has no formal buy-box (`references/screening-benchmarks.md`) — don't invent house
  criteria; the ranges there are explicitly general market context, not policy.
- The screener is the default deliverable; the full underwriting model
  (`assets/model_template_notes.md`) is optional/secondary, built only post-vote. Don't make the
  scripts so elaborate that running a screen stops being fast — a 48-hour deadline is the whole
  point.
- REAP invests as an LP, not a GP — every return calc is post-promote, investor-level. Don't
  build anything that reports project-level returns as if they were REAP's own.

## Suggested order of operations for this session
1. Skim `HANDOFF_CONTEXT.md` and all of `references/*.md` for full context (10-15 min well spent).
2. Task 1 (`fred_rate.py`) — quick win, validates the scripts-folder pattern end to end.
3. Task 5 (`pdf_chart_extract.py`) — highest-value, hardest, do it while context is fresh.
4. Task 4 (`cap_rate_search.py`) — depends on #5 for full value, but can ship a text-only version
   first and layer chart extraction in after.
5. Tasks 2, 3, 6, 7 — roughly independent, parallelizable if you want to batch them.
6. Task 8 only when told there's a live REAP OS deal to test against.
