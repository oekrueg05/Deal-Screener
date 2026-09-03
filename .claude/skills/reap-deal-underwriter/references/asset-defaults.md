# Default Assumptions by Asset Type

Use ONLY when the deal materials don't specify a value. Always flag defaulted values — at the
screen stage, that means naming them plainly in the screener's Assumptions/flags; if a deal
reaches the deep-dive model stage, that also means yellow fill in the model and a line in the
memo's "Assumptions Used" section. These are market-standard starting points, not REAP house
views — update this file as REAP directors or Vito give better guidance.

## Multifamily
- Opex ratio: 35-45% of EGI (use 40% if no further signal)
- Management fee: 3-4% of EGI
- Capital reserves: $250-350/unit/year
- Annual rent growth: 3%
- Annual expense growth: 3%
- Exit cap rate: entry cap rate + 25-50 bps
- Cost of sale: 1.5-2%
- Typical hold period: 5 years

## Office
- Opex ratio: 40-50% of EGI (varies widely by lease structure — gross vs. NNN)
- Management fee: 3% of EGI
- Capital reserves: $0.20-0.40/SF/year
- Annual rent growth: 2-3%
- Exit cap rate: entry cap rate + 50-75 bps (office cap rates less predictable — flag prominently)
- Typical hold period: 5-7 years

## Industrial
- Opex ratio: 15-25% of EGI (often NNN — tenant pays most opex)
- Management fee: 2-3% of EGI
- Capital reserves: $0.10-0.20/SF/year
- Annual rent growth: 2.5-3.5%
- Exit cap rate: entry cap rate + 25-50 bps
- Typical hold period: 5-7 years

## Retail
- Opex ratio: 20-35% of EGI (depends on NNN vs. gross)
- Management fee: 3-4% of EGI
- Capital reserves: $0.15-0.30/SF/year
- Annual rent growth: 2-3%
- Exit cap rate: entry cap rate + 25-50 bps
- Typical hold period: 5-7 years

## Debt (all asset types, absent better data)
- LTV: 65%
- Rate: use current prevailing market rate — search for it rather than assuming; flag if
  estimated
- Amortization: 30 years
- Interest-only period: 0-2 years depending on business plan (value-add = IO; stabilized = none)

**Floating-spread OMs (e.g. "7-Year Treasury + 140 bps") that also give a full projected cash
flow table:** these two things can disagree — the OM's own debt service numbers imply a specific
fixed rate as of when they built the model, which may be stale by the time you're underwriting.
At the screen stage, a quick check is enough: search today's value of the named index, compute
the current rate off the stated spread, and compare it against the rate the OM's own DSCR/return
figures imply at a glance — flag a material gap as a rate-risk factor in the screener without
fully reconciling the two. Save the precise back-out (replicating the OM's cash flows exactly off
an implied rate) for the deep-dive model stage, where it belongs.

## When asset type isn't covered here
Ask the student for the relevant ratios rather than guessing — don't extend these numbers to
asset types they weren't built for (e.g., hospitality, self-storage, land).
