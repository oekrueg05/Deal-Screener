# OM Claim Verification (any asset type, any market)

Every OM contains specific, checkable claims — not just the exit cap rate — presented as fact by
a sponsor with an obvious incentive to make the deal look good. This file is a set of **claim
categories** that show up in nearly every OM regardless of whether it's multifamily, office,
retail, industrial, hospitality, or a ground-up development — not a fixed checklist tied to any
specific deal or asset type. Which categories actually apply, and how deep to go on each, depends
entirely on what's present and material in the specific OM in front of you.

## Verification scripts (Claude Code only)
`scripts/` has small, tested Python scripts that harden five of these nine categories (1, 2, 5, 6,
9 — including both of the always-run ones) against a real public source instead of a hopeful web
search (see each category below for which script and how). `scripts/verified_data_cache.py`
caches any verified figure by (category, market, asset_tier) so a repeat market doesn't need a
fresh search on the next deal. None of this applies in a chat-only environment without code
execution — fall back to web search there, same as before. Categories 3, 4, 7, and 8 have no
script yet; still use a targeted web search for those.

## How to use this file
Two categories are not a judgment call: **2 (yield/cap rate)** and **9 (sponsor background)** run
on every single deal, regardless of how clean the rest of the OM looks — every deal has a cap
rate assumption and every deal has a sponsor, so neither is ever "not applicable." Skipping either
because nothing else about the deal raised a flag defeats the point; the flag is often exactly
what a search like this is for.

For the remaining seven categories, scan the OM for claims falling into them and, for each one
that's present *and* material to the return case, verify it against a live public source before it
goes into the screener as accepted fact rather than a sponsor's assertion. Skip categories that
don't apply — a stabilized acquisition won't have entitlement claims to check; a raw land deal
won't have existing rent comps; an industrial deal shouldn't get an apartment rent index applied
to it. This is a judgment call on relevance and depth per deal, not a mandatory run-through — the
screener still has to stay fast (see `screener-format.md`'s speed-over-completeness principle).
Categories 2 and 9 are the exception to that judgment call, not the rule.

## Categories

### 1. Financing rate / index
Any assumed interest rate tied to a named index (Treasury, SOFR, Prime) — verify the index's
actual current value from a primary source rather than a news article's restated figure. Applies
to any deal with debt, any asset type.

**In Claude Code:** run `scripts/fred_rate.py --series DGS7` (or `DGS10`, `SOFR`, etc.; add
`--spread-bps` for an OM's "index + spread" language) — pulls the latest published value straight
from FRED, dated and sourced. Requires a free `FRED_API_KEY`
(https://fred.stlouisfed.org/docs/api/api_key.html). In chat without code execution, fall back to
a targeted web search.

### 2. Yield / cap rate
Covered in detail in `screening-benchmarks.md`. Search for the deal's actual market *and* the
relevant asset-class/quality tier for whatever asset type this deal is (multifamily, office,
retail, industrial, hospitality) — never a generic blended national figure, and never a tier
that doesn't match the asset type in front of you.

**In Claude Code:** use `WebSearch` to find candidate market-specific reports first, then run
`scripts/cap_rate_search.py --url <candidate> --market <market> --asset-tier <tier>` to fetch and
score every percentage figure in each candidate by proximity to cap-rate/market/tier language. If
a PDF candidate reports no text match, it says so and points at `scripts/pdf_chart_extract.py`
(see category 6's cousin note below) rather than silently giving up. Check
`scripts/verified_data_cache.py get --category cap_rate --market <market> --asset-tier <tier>`
first — a repeat market from an earlier deal this semester may already be cached; `... set ...`
the result afterward so the next deal in that market doesn't need a fresh search.

### 3. Growth assumptions (revenue, expense)
Whatever growth rate the OM assumes for its primary revenue line and for expenses — check against
a real, asset-type-appropriate public index. The index has to match the asset type: an apartment
rent trend index (e.g. Zillow Observed Rent Index, Apartment List) for multifamily is not the
right check for an industrial or office deal, which need their own asset-type-specific asking-rent
or absorption reporting. For expense growth generally, a regional CPI or published expense-growth
benchmark applies regardless of asset type.

### 4. Comparable sales/rents cited in the OM
If the OM names specific comparable properties (rent comps, sale comps, whatever the asset type's
equivalent is), spot-check whether those named properties' current terms still match what the OM
states. OMs get stale between when they're built and when they're read, or are occasionally
curated favorably. Applies to any asset type that uses named comps to justify pricing.

### 5. Location/market claims made in prose
Employer counts, population/demographic trends, walkability, submarket vacancy, traffic counts —
these read as narrative but are usually checkable: Census/BLS have free APIs for population and
employment data; Walk Score has a public API; submarket vacancy is often published by local CRE
associations, brokerages, or regional planning bodies. Applies to any asset type, since every OM
makes some version of a "why this location" argument.

**In Claude Code:** run `scripts/census_lookup.py --geo "<City, ST>" --metric population` (also
`median_income`, `population_growth`, `unemployment_rate`) for population/income/employment claims
specifically — pulls from Census ACS and BLS LAUS directly. Submarket vacancy, walkability, and
traffic-count claims still need a targeted web search; there's no free API wired up for those yet.

### 6. Physical/environmental risk
Flood zone status and environmental history — FEMA flood maps and, where available, state
environmental agency records are public and free. Matters for any property type, and increasingly
material given rising insurance costs nationally.

**In Claude Code:** run `scripts/fema_flood_check.py --address "<property address>"` — geocodes
the address and checks it against FEMA's National Flood Hazard Layer directly, returning the zone
and whether it falls in the mapped Special Flood Hazard Area. No feature returned isn't
automatically "no risk" — the script flags that ambiguity explicitly rather than reporting a false
clean bill of health. State environmental agency records still need a manual/web search; nothing
wired up for those yet.

### 7. Entitlement / deal-status claims
Any claim about where a deal stands procedurally — a signed purchase agreement, a pending
TIF/development agreement, a rezoning or variance in progress, a permit status — is often
checkable against public record: city council or planning commission meeting minutes, permit
databases, county recorder filings. Applies to any deal with a pending approval or
public-private structure, regardless of asset type.

### 8. Supply pipeline / competitive set
Whatever the OM says about new supply coming to the submarket — check against public permit data
or a planning department's pipeline where available, rather than trusting the sponsor's
self-reported framing of how much competing product is coming. Applies to any income-producing
asset type, since new supply is a real risk to every one of them.

### 9. Sponsor background — always run, every deal, no exceptions
A basic news/litigation search on the sponsor entity and named principals — standard practice for
an institutional LP's diligence. This is one of the two categories in this file that isn't a
judgment call (the other is cap rate, category 2): every OM has a sponsor, so this always applies,
and it always gets run regardless of how the rest of the deal reads. A clean-looking OM is exactly
the case where a background check is most likely to be the thing that changes the recommendation
— don't reason your way out of running it because nothing else raised a flag.

**In Claude Code:** `WebSearch` for `"<sponsor entity>" lawsuit OR litigation OR SEC OR
bankruptcy` (and the same per named principal), then run `scripts/sponsor_background_check.py
--sponsor "<entity>" --principal "<name>" --url <candidate> --url <candidate>...` to fetch each
candidate and flag sponsor/principal mentions near litigation-risk language. Reports "found" (with
cited snippet) or "nothing found" explicitly — treat "nothing found" as a disclosed limitation of
the search, not a verified clean record.

## Discipline
- Only check what's actually material and present in this specific OM — forcing an irrelevant
  category wastes the screener's limited length budget on something that doesn't move the
  recommendation. This rule is about categories 1, 3-8; categories 2 and 9 run regardless (see
  "How to use this file" above).
- Cite the specific source, same discipline as the cap rate check — never present a verified
  number without naming where it came from.
- If nothing checkable turns up after a reasonable search, say so plainly in Unknowns rather than
  skipping the category silently — the absence of verifiable public data is itself worth flagging,
  especially for categories like entitlement status where a diligent LP would expect to find
  something.
- Prioritize whichever category's claim is most load-bearing for the return case in front of
  you — the point is catching what would actually change the Pursue/Pass call, not exhaustiveness
  for its own sake.
