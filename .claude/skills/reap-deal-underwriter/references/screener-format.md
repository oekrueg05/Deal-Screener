# REAP Deal Screener Format

This exists to help a REAP student form their own opinion, fast, for a real 48-hour vote. Vito
presents a deal in class with a SWOT (Strengths, Weaknesses, Opportunities, Threats) and an
Unknowns list on the board; each analyst has 48 hours to land on Pursue or Pass, and the class
decides by majority vote. This document is that prep work — not a generic memo, and not a
condensed version of a full underwriting memo. It mirrors the actual classroom framework so a
student can walk in and hold their own in the discussion, not translate between two formats.

This is the **default deliverable for every deal Vito sends**. The full model
(`assets/model_template_notes.md`) and its optional deep-dive memo (`references/memo-format.md`)
are a different, later thing — post-vote diligence for a deal the class actually decides to pursue
with real capital, not part of forming the vote itself.

## Citations

Every number or claim pulled from the OM gets a page citation, inline, right where it's used —
`(p. 38)` or `(pp. 38-39)` if a figure is assembled from more than one page. This applies
everywhere in the document: Snapshot, the Return section, every row of Screen Checks, every SWOT
bullet, every Unknown. The point is that anyone reading this on their phone in the room can flip
straight to the source page and check it themselves, mid-discussion, without having to search the
whole OM — don't make them take the number on faith.

This isn't optional for the figures that carry the recommendation (return metrics, DSCR, exit
cap, basis) — if a number in the Screen Checks table or the Return section doesn't have a page
next to it, go find the page before delivering the screener, don't ship it uncited. A number
computed by REAP (e.g. the LP-level IRR after applying the promote) instead cites the OM page(s)
the *inputs* came from, since the computed figure itself doesn't live on any single page.

Externally-verified figures (cap rate, sponsor background, census data, etc. — see
`references/claim-verification.md`) get their own source citation the same way they already do
(source name, and a page number too when the source is itself a paged document, e.g. a PDF cap
rate survey) — those aren't OM page citations, don't label them as if they were.

## Structure

**[Deal Name] — Screener**
Received from Vito: [date] | Analyst: [student name] | Vote due: [48 hrs from date received,
or the actual deadline if the student states one]

**MY RECOMMENDATION: PURSUE / PASS**
One bolded line. This is a binary call, matching the actual vote — no third option. Follow it
with a single sentence naming the 1-2 factors that decided it. If it's genuinely close, say so
("Lean Pursue, low conviction — see Unknowns") but still commit to one side; "it depends" isn't a
usable input to a majority vote.

**Snapshot** (3-4 lines)
Price, units/SF, asset type, location, going-in/stabilized yield, occupancy or lease-up status.

**REAP's Estimated Return (LP-level, post-promote)**
The number that actually matters: REAP's likely IRR and equity multiple after the sponsor's
promote, at the share class REAP would realistically enter given its typical check size — not
the project-level headline figures the OM leads with. State the assumed share class and its
split terms in one line. If the OM doesn't disclose enough to model the waterfall precisely, take
a swing at it anyway and flag what's estimated — list the promote terms themselves under
Unknowns if they're genuinely undisclosed, don't just skip the calculation. If there's no
promote layer at all (REAP investing directly), use project-level figures and say so.

**Screen Checks**
A compact table (or tight bullets if a table doesn't fit the context): one line per metric from
`references/screening-benchmarks.md` — metric, REAP's number (with its OM page citation), the
reference range, and a pass/marginal/fail/insufficient-data read. This is the "show your work"
behind the recommendation — keep each line to the number and the call, not a paragraph of
explanation.
Always include a line verifying the exit cap (and going-in/stabilized yield, if applicable)
against real market data via web search — cite what was found briefly (e.g., "~5.0-5.5% per
[source]") rather than just restating the OM's own assumption back at itself as if that settles
it. Add a line for any other claim verified per `references/claim-verification.md` when it turned
up something worth showing (e.g., a growth-rate assumption checked against a public rent index, a
comp that turned out stale, an entitlement status confirmed or contradicted by public record) —
same discipline, same format: the number, the source, the read.

**SWOT**
Four short bullet groups, matching the board format exactly:
- **Strengths** — what's working in the deal's favor (proven occupancy/lease-up, new
  construction limiting near-term capex, strong submarket fundamentals, sponsor track record or
  scale/optionality, favorable basis vs. replacement cost, etc.)
- **Weaknesses** — what's working against it that's inherent to the deal itself (thin going-in
  yield, aggressive rent growth assumptions, DSCR running tight, high basis vs. comps, etc.)
- **Opportunities** — upside not baked into the base case (repositioning potential, submarket
  momentum, adjacent-phase optionality with the same sponsor, refinance/rate-decline upside, etc.)
- **Threats** — external factors that could hurt the deal regardless of execution (submarket
  supply pipeline, rate risk on refinance/floating debt, cap-rate expansion risk, macro/employer
  concentration risk, etc.)

The Screen Checks table above is the evidence; SWOT is the synthesis — don't just restate each
Screen Checks row as a bullet. Reference `references/screening-benchmarks.md` for context on
where the numbers land (general institutional LP norms, not REAP policy — REAP has no formal
buy-box), but write the SWOT in plain analyst language. Keep each bullet group to 2-4 items —
this needs to be readable on a board/in a discussion, not exhaustive.

**Unknowns**
What the OM doesn't tell you and REAP hasn't independently verified — the questions worth raising
in class or asking Vito directly before the vote, not risks you've already assessed. This is
where every defaulted/estimated assumption from the screen belongs (e.g., "OM doesn't disclose a
fixed interest rate, only an index+spread — backed out an estimate, actual number unknown until
rate-lock," "1031/Class E fee terms not specified," "no sponsor track record disclosed"). Distinct
from Weaknesses: a Weakness is a known negative; an Unknown is something you can't yet assess
either way. Keep to 2-4 items.

## Length
Short enough to prep for a real discussion in a few minutes, not a document a student has to
study. If SWOT + Unknowns is running long, that's a sign to cut to what actually matters for the
vote, not to keep everything "for completeness."

## Tone
Direct, like notes you'd actually bring into the room. Commit to the recommendation — the whole
point is helping a student reach and defend an opinion in 48 hours, not hedge every point.

## Visual formatting
This gets read fast, often on a phone, so it should be scannable at a glance, not just short.
- Open with the verdict as its own bolded heading line with a symbol — `## ✅ PURSUE`,
  `## ❌ PASS` — not buried in a paragraph. Follow immediately with the one-sentence reason in
  italics or as a blockquote, then a horizontal rule (`---`) before the rest of the document.
- Right under that, add a compact stat line — 3-5 of the headline numbers (LP IRR, equity
  multiple, DSCR low point, hold period) as a single bolded row separated by `·` or as a tiny
  table — so the numbers that matter are visible before anyone reads a word of prose.
- Use a horizontal rule (`---`) between every major section (Snapshot, Return, SWOT, Unknowns) —
  the visual break matters as much as the header for fast scanning.
- In the Screen Checks table, lead each "Read" cell with a symbol (✅ pass, ⚠️ marginal/flag,
  ❌ fail/below floor) before the words — a column of symbols is scannable in a way a column of
  adjectives isn't.
- Inside SWOT, give each of the four groups its own `###` subheading (not just a bolded label in
  a paragraph) so the board's four-quadrant structure is visually obvious, not just implied by
  bullet grouping.
- Bold the key figure or driver at the start of each bullet (e.g., "**DSCR is thin exactly when
  it matters most** — ...") so a skim of just the bolded openers gives the gist.
- Never sacrifice the content rules above (bullet caps, length budget) for decoration — formatting
  makes the required content easier to scan, it doesn't earn room for more of it.
- Keep page citations short and inline — `(p. 38)` right after the number, not a footnote or an
  endnotes section. A citation should never be long enough to break the scannability of a bulleted
  line or a table cell.
