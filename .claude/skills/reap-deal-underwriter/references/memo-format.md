# Deal Memo Format (optional, deep-dive only)

**This is no longer the default deliverable.** Every deal gets the fast screener
(`references/screener-format.md`), which already carries the SWOT, Unknowns, and Pursue/Pass
recommendation the student needs for the class vote — this memo is the optional deeper write-up
for a deal the class actually votes to pursue, built as REAP moves toward a real capital
decision, per SKILL.md step 9.

One page. This is a teaching artifact and a deal-log entry, not a full IC memo — keep it tight.

## Structure

**[Deal Name] — [Asset Type], [Location]**
Received from Vito: [date] | Analyst: [student name]

**Deal Snapshot** (3-4 lines)
Price, size, current vs. market rent, occupancy, headline return metrics (IRR, equity
multiple, cash-on-cash Year 1). If the OM itself states headline returns (common for sponsor
syndication decks), always rebuild the cash flows independently from the input assumptions
rather than copying the OM's stated IRR/multiple into the model — then note here whether the
two land close together or diverge, in one sentence, pointing to Assumptions Used for why.

**Deal Thesis** (2-3 sentences)
What's the story — stabilized income play, value-add repositioning, development, etc. Pull
this from the OM/materials if stated; otherwise infer from the numbers and say so.

**Assumptions Used** (bulleted list)
Every defaulted/flagged assumption from the model, with the value used and why (e.g.,
"Opex ratio: 40% — not itemized in OM, used multifamily default"). This is the most important
section for teaching value — it's where a student sees what they don't know yet.

**Key Strengths** (2-3 bullets, hard cap — see Length below)
What's working in the deal's favor — in-place occupancy/lease-up already proven, new
construction limiting near-term capex, strong submarket fundamentals, sponsor track record or
scale/optionality (e.g. rights on adjacent phases), favorable basis vs. replacement cost, etc.
Same analytical tone as Key Risks — evidence-based, not a sales pitch.

**Key Risks** (2-3 bullets, hard cap — see Length below)
Whatever stands out — rent growth assumptions look aggressive relative to submarket, debt
maturity mismatched to hold period, deferred maintenance not reflected in capex reserve, etc.
Analytical, not a verdict — no "pass" or "pursue" recommendation.

Two risk types get folded in here when they apply, and count against the same 3-bullet cap
rather than extending it:
- **DSCR covenant breach** (from the Debt Schedule tab's covenant check) — if any year dips
  below the flagged threshold, this is a risk bullet, not just a highlighted cell.
- **REAP's position as a limited (non-controlling) equity partner**, when the deal has a
  promote/waterfall — which share class REAP would likely fall into (by check size) and its
  specific split terms, the resulting investor-level IRR/multiple after the promote (vs. the
  project-level figures the rest of the memo focuses on) pulled directly from the OM's
  waterfall/investor-return tables (don't estimate them), and the lack of control over
  refinance/capex/sale-timing decisions.

If more candidate risks surface than the cap allows, prioritize in this order and cut or merge
the rest: (1) DSCR covenant breach, (2) financing/rate risk, (3) REAP's LP/waterfall position,
(4) market/supply or other structural risk. A risk that doesn't make the cut can still live in
Assumptions Used if it's assumption-driven, or get a half-sentence folded into an adjacent bullet
— don't quietly grow the list past 3.

**Outlook** (2-3 sentences)
What this deal illustrates about the market/asset class right now — this is the "how the
industry works" payoff for the student, tie back to what's observable in the numbers.

## Length
This is a one-page, two-minute read — that budget is a hard constraint, not an aspiration, and
it has to hold even as more required content (Key Strengths, LP/waterfall notes, DSCR flags) gets
folded in. Concretely: Deal Snapshot stays at 3-4 lines, Deal Thesis and Outlook stay at 2-3
sentences each, and Key Strengths + Key Risks combined never exceed 6 bullets total (3+3). If a
deal has enough going on that everything relevant won't fit, cut detail rather than length —
Assumptions Used can absorb overflow since it's already itemized and expected to run longer on
complex deals.

## Tone
Direct, specific, no filler. Write like an analyst handing this to the next person who picks
up the deal, not like a sales pitch.

## Visual formatting
Same scannability standard as the screener (`references/screener-format.md`) — this is a longer
document, so the visual structure matters even more for someone skimming it.
- Use a horizontal rule (`---`) between every major section (Deal Snapshot, Deal Thesis,
  Assumptions Used, Key Strengths, Key Risks, Outlook) so sections are visually distinct, not
  just header-delimited.
- Give Key Strengths and Key Risks each a symbol in the header — `## 💪 Key Strengths`,
  `## ⚠️ Key Risks` — and bold the key driver at the start of every bullet in both, same as the
  screener's "Why" section.
- If this memo follows a screener for the same deal, open with a one-line stat bar like the
  screener's (LP IRR, equity multiple, DSCR range, hold period) so the two documents are visually
  consistent and someone can move between them without re-orienting.
- Assumptions Used reads well as a table (Field / Value / Source) when there are more than ~4
  rows — cleaner to scan than a long bullet list once it grows.
- Never sacrifice the content rules above (length budget, bullet caps) for decoration —
  formatting makes the required content easier to scan, it doesn't earn room for more of it.
