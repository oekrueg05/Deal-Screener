# Standard Deal Input Schema

Every deal gets mapped to these fields. Fields marked **[SCREEN]** are what the fast screener
needs — pull these first and don't stall the screen chasing the rest. Note the OM page number for
each field as it's pulled, not after the fact — the screener (`references/screener-format.md`)
cites the source page for every figure it uses, and it's far easier to capture that page number
during this extraction pass than to go re-find it while writing the document. Fields marked **[DEEP-DIVE]**
only matter if the deal clears the screen and a full underwriting model gets built (SKILL.md step
9) — skip them at the screen stage. Mark any [SCREEN] field not found in source materials as
MISSING and resolve via `asset-defaults.md`; [DEEP-DIVE] fields can stay MISSING until/unless the
deep-dive stage is actually reached.

## Deal Basics — all [SCREEN]
- Deal name / property name
- Sponsor / GP (name of the entity offering the deal, if disclosed — e.g. an OM's issuer)
- Asset type (multifamily, office, industrial, retail, mixed-use, etc.)
- Location (market, submarket if known)
- Unit count / SF (as applicable to asset type)
- Asking price
- Source: Vito
- Date received
- Analyst (student name)

## Revenue — [SCREEN]: headline only
- Stabilized/proforma rent (per unit/SF, or total) — [SCREEN]
- Current occupancy % / lease-up status — [SCREEN]
- Annual rent growth rate assumption, if the OM states its own return case off one — [SCREEN]
- Current in-place rent, market rent (if different from stabilized), itemized other income
  (parking, storage, RUBS) — [DEEP-DIVE]

## Expenses — [DEEP-DIVE] except where noted
- Total operating expenses or opex ratio, if needed to sanity-check the OM's stated NOI —
  [SCREEN, lightweight only — don't rebuild an itemized expense stack to screen a deal]
- Property taxes, insurance, itemized management fee, capital reserves, annual expense growth
  rate — [DEEP-DIVE]

## Debt — [SCREEN]: enough to compute DSCR and rate risk; rest is [DEEP-DIVE]
- Loan-to-value (LTV) or loan amount — [SCREEN]
- Interest rate (or the index+spread if floating) — [SCREEN]
- Whether financing is locked or floating — [SCREEN], drives the rate-risk flag
- Amortization period, interest-only period, loan term/maturity, full monthly amortization
  detail — [DEEP-DIVE]

## Exit — [SCREEN]
- Hold period (years)
- Exit cap rate — [SCREEN], and verify against current market cap rates for that specific
  metro/submarket and asset type via web search (see `references/screening-benchmarks.md`);
  don't take the OM's assumption at face value
- Cost of sale (%) — [DEEP-DIVE] unless it's large enough to move the LP-level return materially

## Waterfall / Promote — [SCREEN], this is the core of the screen
If the deal is structured as an equity syndication with a GP/LP split, this section is what makes
the LP-level return calculation possible — treat it as essential, not optional, even at the
screen stage:
- Share classes and minimum investment per class (e.g. Class A $2M+, Class B under $2M)
- Preferred return hurdle
- Tiered IRR hurdles and the LP/GP split at each tier
- Which class REAP would fall into given its typical check size — call this out explicitly,
  since it determines which split terms apply to REAP's actual return, not just the project's
- Any class the OM acknowledges but leaves partially undefined (e.g. a 1031/UPREIT class with
  "adjusted fees to compensate Sponsor" and no number given) — note it as partially disclosed
  rather than omitting it; flag as a diligence gap in the screener if REAP's likely class is the
  one affected

## Output Metrics (computed, not input)
- **[SCREEN]** REAP's LP-level IRR and equity multiple (post-promote) — the figures actually
  checked against the screening benchmarks
- **[SCREEN]** Project-level IRR/multiple, for reference/comparison only
- **[SCREEN]** DSCR — at minimum the low-water-mark year, to check against the DSCR covenant
  threshold; full year-by-year detail is [DEEP-DIVE]
- **[SCREEN]** Going-in/stabilized cap rate, exit cap rate, and the spread between them
- Year-by-year NOI, cash-on-cash by year, full DSCR schedule — [DEEP-DIVE]
