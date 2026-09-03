---
name: reap-deal-underwriter
description: Help a Marquette REAP student form a fast, defensible Pursue/Pass opinion on a deal Vito presents in class, ahead of a real 48-hour deadline and majority-vote decision. Vito presents each deal with a SWOT (Strengths/Weaknesses/Opportunities/Threats) and an Unknowns list on the board — this skill builds that same artifact from an OM, rent roll, or raw numbers. This is a screener, not a full underwriting exercise. Use this any time a deal comes in from Vito or a student asks to "screen this deal," "should we pursue this," "run the numbers," or "underwrite this deal." Every deal gets screened; a full editable underwriting model is optional, built only for a deal the class votes to pursue or on explicit request. Use this instead of an ad hoc spreadsheet or generic memo when the request involves real estate pro forma inputs, a pursue/pass call, NOI/cash flow projections, IRR/equity multiple/DSCR, or a REAP deal-log entry.
---

# REAP Deal Screener

REAP's actual process: Vito presents a deal in class with a SWOT and an Unknowns list on the
board, and each analyst has 48 hours to land on Pursue or Pass before the class decides by
majority vote. This skill exists to help a student get to that opinion fast — it builds the same
SWOT + Unknowns artifact from whatever materials Vito hands out, screened off what REAP would
actually receive as a limited equity partner (not the project-level numbers the OM leads with).
Every deal gets screened and logged. A full underwriting model is a separate, later thing built
only for a deal the class votes to pursue, not part of forming the vote itself.

## Workflow

1. **Check for the REAP OS deal inbox first.** REAP OS exposes an MCP server that analysts
   connect to. Before asking the student to paste or upload anything, check whether a REAP OS
   connection is available (on either surface — see `references/mcp-integration.md`) and use it
   to look up the deal — by name if the student gave one, or by pulling the most recent
   unprocessed entry in the deal inbox if they just said "screen the new deal Vito sent." Only
   fall back to asking the student for materials directly if no REAP OS connection is available
   or the deal isn't found in the inbox.

2. **Read the deal materials.** Whatever came back from REAP OS, plus anything the student
   pastes or uploads directly. Extract what's needed using `references/input-schema.md` as a
   guide — pull the headline financial figures, the waterfall/promote terms, debt terms, and
   exit assumptions; don't chase every itemized expense line the way a full underwrite would.
   Check the incoming deal name (and location/unit count) against `deal_log.csv` before assuming
   it's new — if it matches an existing deal, this is a revision; follow the Revisions section of
   `references/deal-log-format.md`.

3. **Fill essential gaps with defaults, and flag every one — as Unknowns, not silent guesses.**
   For any field the screen needs that the source materials don't cover, pull the default from
   `references/asset-defaults.md`, use it to keep the analysis moving, but list the underlying
   gap in the screener's Unknowns section rather than presenting the default as a known fact. A
   screen tolerates real estimation — the point of Unknowns is to surface it, not eliminate it.

4. **Compute REAP's LP-level return.** REAP checks in as a limited, non-controlling partner —
   apply the OM's disclosed waterfall/promote to get REAP's actual investor-level IRR and equity
   multiple at the share class it would realistically enter (by check size), not the
   project-level figures the OM headlines. If no promote layer exists, use project-level figures
   and say so. If the waterfall terms themselves are undisclosed, note that under Unknowns rather
   than skipping the calculation.

5. **Verify the OM's checkable claims against live public sources — cap rate included, but not
   limited to it.** Don't just benchmark the OM's numbers against generic ranges, and don't limit
   verification to the exit cap. Any specific, checkable claim the OM makes — financing rate,
   revenue/expense growth, cited comps, location/market claims, entitlement status, supply
   pipeline, sponsor background — is worth a targeted search against a live public source rather
   than accepted at face value. See `references/claim-verification.md` for the full set of claim
   categories and which public sources fit each (this generalizes across every asset type — the
   category framework is universal even though which specific check applies depends on what's
   actually in the OM in front of you). The exit cap check specifically is detailed in
   `references/screening-benchmarks.md`, since it's usually the single highest-leverage one (most
   OMs' terminal value, and therefore most of the return case, hangs on it) — always run that one.
   Beyond it, use judgment on which other categories are material enough to this specific deal to
   be worth the search time; this has to stay fast, not turn into exhaustive due diligence. Cite
   what was found; if nothing specific enough turns up, say so rather than skipping it.

6. **Build the SWOT and Unknowns, and land on a Pursue/Pass recommendation.** Use
   `references/screening-benchmarks.md` for context on where the numbers land (general
   institutional LP norms — REAP has no formal buy-box, so frame it as market context feeding
   your judgment, not a policy test). Sort what you've found into Strengths / Weaknesses /
   Opportunities / Threats plus a separate Unknowns list, then commit to one recommendation:
   Pursue or Pass — binary, matching the actual vote. If it's genuinely close, say so, but still
   pick a side.

7. **Write the screener.** Follow `references/screener-format.md` exactly — it mirrors the board
   format (SWOT + Unknowns) so the student can walk into the discussion without translating
   between formats. Short enough to prep from in a few minutes.

8. **Log the deal.** If the REAP OS connection is available, write the screener's summary fields
   back to REAP OS per `references/mcp-integration.md`. Always also append a row to the local
   `deal_log.csv` per `references/deal-log-format.md` as a fallback record, whether or not the
   MCP write succeeded — including the vote deadline and (once known) the class's actual majority
   outcome if the student reports it back. Use the file-naming and revision conventions there —
   never overwrite a prior deal's files.

9. **Deliver the screener.** It goes to outputs as markdown (or docx, per student preference).
   `deal_log.csv` is a background record — keep appending to it every deal, but don't present or
   deliver it as an output file unless the student specifically asks for it.

10. **Full underwriting model — optional, later, only for deals the class votes to pursue.** Only
    build the full multi-tab editable Excel model (`assets/model_template_notes.md`) and its
    deep-dive memo (`references/memo-format.md`) after a deal actually gets voted to pursue and
    REAP is moving toward a real capital decision, or on explicit request. This is post-vote
    diligence — it has nothing to do with forming the 48-hour opinion, and building it
    automatically would defeat the point of a fast screener.

## Important notes

- **The deliverable is a vote-ready opinion, not a report.** The student needs to walk into a
  discussion and defend Pursue or Pass in 48 hours — everything here is in service of that, not
  documentation for its own sake.
- **Match the board format exactly.** SWOT + Unknowns is the actual framework the class uses;
  don't substitute a different structure (a generic "strengths/risks" list, an IC-memo format,
  etc.) just because it's a natural thing to write for a real estate deal. The student needs
  something that maps directly onto what's already on the board.
- **Screen off REAP's actual position, not the OM's headline.** REAP is a limited, non-controlling
  partner in almost every deal Vito sends — the recommendation has to be based on REAP's
  post-promote, investor-level return, never the project-level IRR/multiple the sponsor is
  selling.
- **Don't take the OM's claims at face value where they're checkable.** The OM is written by a
  party with an obvious incentive to make the deal look good. Cap rate always gets verified
  against live public data (see `references/screening-benchmarks.md`); other checkable claims —
  growth assumptions, cited comps, location claims, entitlement status, sponsor background — get
  the same treatment when material to the deal in front of you (see
  `references/claim-verification.md`). This applies to any asset type; which specific claims are
  worth checking depends on what's actually in the OM, not a fixed list.
- **REAP has no formal buy-box.** `references/screening-benchmarks.md` holds general
  institutional LP reference ranges, not REAP-approved criteria — they inform the SWOT/Unknowns
  judgment call, they don't replace it with a pass/fail test.
- **Missing data goes in Unknowns, not silently into the model.** Vito's deals will often be
  partial. Apply a default to keep the analysis moving, but the gap itself belongs in the
  screener's Unknowns section — that's exactly the kind of thing worth raising in the class
  discussion before the vote.
- **Consistency across deals matters more than sophistication on any one deal.** Same screener
  format, same benchmark checks, same deal-log columns every time — that's what makes the log
  useful as students compare deals and track REAP's hit rate over a semester.
- **The REAP OS connection is per-analyst and per-surface.** Don't assume it's present, don't
  hardcode a URL, and never fail the whole workflow if it's missing or a call errors. Degrade
  gracefully to manual input every time.
