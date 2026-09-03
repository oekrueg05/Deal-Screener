# Screening Benchmarks

**REAP does not have a formal buy-box.** There is no set of REAP-approved investment criteria to
screen against, and this file should never be presented as if there were. What follows are
general institutional multifamily/CRE LP benchmarks — reference points from how limited partners
in this asset class typically evaluate a deal — used to give the screener something concrete to
say, not a pass/fail policy test. Every screener built using these must say plainly that they're
general market context, not REAP criteria, since the group hasn't set its own.

## Why LP-level, not project-level

REAP typically checks in as a limited, non-controlling equity partner (Class B or equivalent,
well under most sponsors' Class A minimums). That means REAP's actual return is whatever survives
the sponsor's promote — not the project-level IRR the OM leads with. Compute REAP's investor-level
IRR/multiple, at the share class REAP would realistically enter given its typical check size,
before comparing against anything below. If a deal has no sponsor/promote layer (REAP investing
directly, not as an LP under a GP), use project-level figures and say so.

## General reference ranges (institutional LP norms, not REAP policy)
- IRR (LP-level, post-promote): below ~10% is generally considered weak for the illiquidity and
  risk of a 5-10 year private CRE equity check; above ~13-15% is generally considered strong;
  the range between is where most deals land and where judgment matters most.
- Equity multiple (same hold period): below ~1.5x is thin for a multi-year illiquid hold; above
  ~1.8-2.0x is generally considered attractive.
- DSCR: most agency/bank multifamily lenders require ~1.20-1.25x minimum; a deal projecting
  below that in any year is carrying real covenant/refinance risk regardless of the return.
- Leverage: >80% LTV is aggressive relative to typical bank/agency multifamily terms.
- Basis: acquisition price above replacement cost, or a going-in yield within ~50 bps of the
  assumed exit cap rate, both reduce the margin for error on the return case.

## Cap rate is location-specific — verify it, don't just benchmark it
The ranges above are generic. Cap rates are not — they move by metro, submarket, and asset
class, and an OM's exit cap (and any stated going-in/stabilized yield) is the sponsor's own
assumption, not a fact. This is checkable with a couple of quick, targeted web searches every
time, and it's the single highest-leverage instance of a broader pattern — see
`references/claim-verification.md` for the full set of OM-claim categories worth verifying this
way (financing rate, growth assumptions, cited comps, location claims, entitlement status, supply
pipeline, sponsor background) across any asset type. Cap rate gets its own detailed section here
because it usually drives most of the terminal value in the return calc. It's one of only two
categories worth verifying on every single deal without exception — sponsor background (category
9) is the other — while the remaining categories are judgment calls on relevance per deal:
- **Search for a tiered source first, not a headline national average — and don't gatekeep to a
  short list of big-name brokerages.** CBRE, JLL, Marcus & Millichap, and Cushman & Wakefield all
  publish cap rates broken out by market *and* asset class/quality tier (e.g., "suburban Class
  A," "core," "value-add"), and are a reliable starting point, but they're not the only
  legitimate sources — local/regional brokerages, university real estate centers, county or city
  economic development reports, RealPage, Yardi Matrix, CoStar-sourced market coverage, and
  credible local business-journal reporting citing licensed data can all be just as usable,
  especially for secondary markets the national firms don't break out in detail. What matters is
  the breakout (market *and* asset-class/quality tier), not the logo — a smaller but tiered and
  specific source beats a big-name but blended national headline every time. A generic "US
  multifamily cap rate is 4.7%" headline is almost always a large-metro institutional-core
  average and will make a small suburban or boutique deal look more overpriced (or underpriced)
  than it really is — search past the headline number for the tier/market breakdown, wherever it
  comes from.
- **Search for the deal's actual market by name first, not a proxy.** Many brokerages (Marcus &
  Millichap especially) publish dedicated investment forecast reports for 40-50+ individual
  metros, including secondary ones — Milwaukee, Cincinnati, Kansas City, and similar markets
  usually have their own named report, not just a footnote in a national one. Search for that
  market by name (e.g., "Marcus & Millichap Milwaukee multifamily investment forecast") before
  reaching for a larger nearby metro as a stand-in. Only fall back to a proxy market if a
  genuine search for the actual market turns up nothing usable.
- **A report existing doesn't mean its number is extractable.** Cap rates in these reports are
  often shown as chart/graphic values rather than stated in the prose text, so a web search or
  fetch may surface the report and its qualitative read (e.g., "firming pricing," "resilient
  demand") without the actual percentage being retrievable as text. When that happens, say so
  plainly — cite the report and its qualitative direction, and separately cite whatever
  quantified range you can actually pull (even from a different but reasonable comp, clearly
  labeled as such) rather than blending the two into one number that implies more precision than
  you actually have.

  **In Claude Code:** `scripts/pdf_chart_extract.py --url <report> --out-dir <dir>` pulls the
  embedded chart image(s) out of the PDF (and can rasterize a whole page with `--render-pages`
  when the chart is vector-drawn, not an embedded image) so you can `Read()` them directly and
  read the axis labels/values yourself — the confirmed real case this solves: Marcus & Millichap's
  Milwaukee multifamily report has a genuine per-market cap rate chart that a plain text fetch
  can't see.
- **If you do fall back to a proxy market, label it as exactly that** — not as if it were the
  subject property's own market. "This market isn't individually broken out in [source]; using
  [comp market] as the closest quantified reference point" is honest; presenting the comp
  market's number as if it were the subject market's own figure is not, even if the two markets
  are genuinely similar.
- **Match the asset scale, not just the market.** A 10-20 unit boutique property is not the same
  animal as the 100-300+ unit institutional assets most cap rate surveys are built from — smaller,
  less liquid, less institutionally financeable assets typically trade at a premium (higher cap
  rate, lower value) to the tracked institutional range. Note this adjustment explicitly rather
  than treating the survey figure as directly applicable to a small asset.
- Compare what comes back against the OM's stated exit cap (and stabilized/going-in yield if
  given). If the OM's exit cap sits meaningfully below the relevant tier/market range (adjusted
  for scale per above), that's the sponsor assuming favorable pricing by exit — flag it as a
  real risk. If it's at or above that range, that's a more conservative, defensible assumption —
  say so, it's a point in the deal's favor.
- Cite the specific source and figure, not just "market data" — "CBRE's H2 2025 Cap Rate Survey
  puts suburban Chicago Class A multifamily around 5.0-5.75%" or "the local county's 2026 economic
  development report cites recent suburban multifamily trades in the 6-7% range" are both usable
  citations, from a national brokerage or a smaller regional source alike; "cap rates are around
  5%" with no named source is not. If nothing specific enough turns up after a reasonable search,
  say that plainly rather than forcing a comparison to a mismatched market or asset class.
- This applies to development deals too, even though there's no "going-in" cap rate in the
  acquisition sense — check the exit cap assumption the same way, since that's what the terminal
  value and return case still depend on.

## Using this in the screener
- State the LP-level IRR/multiple and the risk/basis checks plainly, with these ranges as
  context ("this lands below the ~10% range generally considered a weak LP return" rather than
  "this fails REAP's IRR threshold").
- Give a read — Pursue / Pass is the actual binary the vote needs, so land on one — but frame it as the
  analyst's assessment against general market norms, not a policy determination. Name which
  factor(s) drove the read.
- If REAP later sets its own criteria, put them here (or a new file this one points to) and
  drop the "no formal buy-box" framing — until then, don't let a screener imply the group has
  house rules it doesn't have.
