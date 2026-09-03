# Deal Log Format

A running record of every deal screened, so the log is useful across a semester, tracks REAP's
hit rate against the class's actual vote outcomes, and survives senior turnover. Store as
`deal_log.csv` in the working directory unless the student says otherwise; this is also the
structure to hand to REAP OS later if/when it ingests deals directly.

## Columns
- deal_name
- date_received (when Vito presented it in class)
- vote_deadline (date_received + 48 hours, unless the student states a different deadline)
- source (always "Vito" for now, but keep the column general)
- analyst
- asset_type
- location
- price
- units_or_sf
- my_recommendation (Pursue / Pass — binary, matching the actual vote)
- recommendation_drivers (short semicolon-separated list of the 1-2 SWOT/Unknowns factors that
  actually decided it, e.g. "thin LP IRR; undisclosed 1031 fee terms")
- class_outcome (Pursue / Pass / blank — the class's actual majority-vote result, filled in once
  the student reports it back; leave blank until known, don't guess)
- lp_level_irr (REAP's estimated investor-level IRR, post-promote — the figure the
  recommendation is actually based on)
- lp_level_equity_multiple
- share_class_assumed (which class REAP would realistically enter, and its check size/split terms
  in short form, e.g. "Class B, 75/25 to 14% then 50/50")
- project_level_irr (for reference/comparison — not what the recommendation is based on)
- hold_period_years
- key_unknowns (short semicolon-separated list of what's flagged as genuinely unresolved, e.g.
  "interest rate not locked; sponsor track record undisclosed")
- revision (integer, starting at 1 — see Revisions below)
- screener_file_path
- model_file_path (blank unless the class voted to pursue and a full model was built)
- memo_file_path (blank unless the class voted to pursue and a deep-dive memo was built)

## File naming
`[Deal_Name]_Screener.md` (or `.docx`) is the default deliverable for every deal. If a deal gets
voted to pursue and a full underwriting model follows (secondary, optional — see SKILL.md step
9), name it `[Deal_Name]_Underwriting_Model.xlsx` and its memo `[Deal_Name]_Memo.md`. Deal name
space-to-underscore, matching the `deal_name` column exactly. On a revision (see below), append
`_v2`, `_v3`, etc. before the extension on whichever files exist for that pass — never silently
overwrite a prior version's files, even though the deal log only ever gains rows and never loses
them.

## Revisions
Vito will sometimes send a revised OM for a deal already in the log — new pricing, an updated
rent roll, a changed capital stack, or a changed waterfall. Detect this by matching incoming
`deal_name` (and ideally location/unit count) against existing rows before assuming it's a new
deal. When it's a revision:
- Re-run the screen from the revised materials — don't patch the old screener in place. Use the
  versioned file names above.
- Append a **new row** to `deal_log.csv` with `revision` incremented from the prior entry for
  that deal name — never overwrite or delete the earlier row. The log should show the deal's
  history, including how the recommendation changed, not just its latest state.
- In the new screener's Snapshot, add one line noting what changed and how it moved the
  recommendation (e.g. "Revision 2: purchase price reduced from $41.2M to $39.0M — LP-level IRR
  improves from 9.1% (Pass) to 13.4% (Pursue)"). Pull the prior figures from the earlier
  `deal_log.csv` row, not from memory.
- If it's ambiguous whether an incoming deal is a genuine revision or a coincidentally similar
  new deal (e.g. same market, different property), ask the student rather than guessing.

## Behavior
- If `deal_log.csv` doesn't exist in the working directory, create it with headers.
- Append one row per deal screened (including each revision) — never overwrite prior rows.
- Leave `class_outcome` blank at write time; if the student later reports back how the class
  voted, update that specific cell rather than adding a new row — it's the same deal record, just
  completed.
- If asked to summarize or compare deals, check REAP's hit rate (e.g. "how often did my
  recommendation match the class"), or review a deal's history, read from this file rather than
  re-deriving from individual screeners or models.
