# Underwriting Model Structure (optional, post-vote only)

**This is no longer the default deliverable.** Every deal gets the fast screener
(`references/screener-format.md`) to prep the student's 48-hour Pursue/Pass opinion — this full
multi-tab model only gets built after a deal is actually voted to pursue by the class, or on
explicit request, per SKILL.md step 9. Don't build it just because a student's own
recommendation was Pursue — wait for the class outcome, or for the student to ask directly.

Build every deal that reaches this stage with the same tab structure, so models stay comparable
across the deal log.
Follow the xlsx skill's color/number conventions throughout (blue = input, black = formula,
yellow fill = assumption/placeholder cell to flag).

## Tab 1: Deal Summary
- Deal name, asset type, location, price, units/SF (blue inputs, top of sheet)
- Output metrics block, all formulas linking to other tabs: going-in cap rate, exit cap rate,
  levered IRR, equity multiple, average cash-on-cash, DSCR range
- "Assumptions Flagged" mini-table listing every yellow-fill cell elsewhere in the workbook and
  its tab/cell reference, so a reviewer can jump straight to what needs checking

## Tab 2: Assumptions
- All revenue, expense, debt, and exit assumptions from the input schema, one per labeled row
- Yellow fill on any cell using a defaulted value; a "Source" column noting "OM" / "Vito email"
  / "Default — [asset type] multifamily opex" etc. for every row

## Tab 3: Pro Forma (Year 1 through Hold Period + Exit)
- Rows: Gross Potential Rent, Vacancy Loss, Other Income, Effective Gross Income, Operating
  Expenses (itemized if available, else single line at the opex ratio), NOI, Debt Service,
  Cash Flow Before Tax
- Columns: one per year of the hold period, plus a Year 0 (acquisition) column
- All cells formulas referencing Tab 2 — no hardcoded year-over-year growth

## Tab 4: Debt Schedule
- Loan amount, rate, amortization, IO period from Tab 2
- Build the amortization **monthly**, then roll it up into annual display rows — don't compute a
  single annual `PMT` off the balance at the start of amortization. A monthly schedule handles any
  IO period length (not just whole years — a 30-month IO period has no clean home in an
  annual-only schedule) and replicates institutional-quality OM debt service far more closely.
  Structure: a hidden/collapsed monthly calc block (beginning balance, interest, principal, ending
  balance, per month for the full hold period) feeding annual summary rows (beginning balance =
  month-1 beginning, interest = SUM of the 12 monthly interest cells, principal = SUM of the 12
  monthly principal cells, ending balance = month-12 ending, debt service = interest + principal,
  DSCR = NOI / debt service). During the IO months, monthly principal is 0 regardless of where the
  IO period falls relative to year boundaries.
- Flag in the memo's Assumptions Used if the resulting annual debt service differs from an
  OM-stated figure by more than ~1%, since that signals a genuine rate/amortization mismatch worth
  surfacing rather than a rounding artifact.
- **DSCR covenant check:** if DSCR in any year falls below the range in
  `references/screening-benchmarks.md` (or a different covenant stated in the OM itself, which
  takes precedence), call it out — this belongs in the model as a highlighted cell (light red
  fill) and gets one bullet in the memo's Key Risks, not just a number left for the student to
  notice on their own.

## Tab 5: Returns
- Equity investment (Year 0), cash flows by year (from Tab 3), reversion value (exit cap
  applied to Year [hold+1] NOI, less cost of sale)
- IRR and equity multiple formulas pulling the full cash flow stream
- Cash-on-cash by year
- **If the OM discloses a waterfall/promote**, add an LP Waterfall block below the project-level
  figures: preferred return hurdle and each IRR tier as its own labeled, formula-driven row
  (referencing the tier rates and splits from Tab 2), computing the LP share of cash flow and
  reversion after each tier. Output investor-level IRR and equity multiple for the share class
  REAP would actually fall into (by check size), alongside the project-level numbers — not as a
  prose aside in the memo, but as real formulas a student can stress-test by changing the tier
  assumptions. If no waterfall is disclosed, skip this block; project-level returns stand alone.
  If a share class exists with terms the OM acknowledges but doesn't disclose (e.g. a 1031/
  UPREIT class with "adjusted fees" left unspecified), list it in Tab 2 with a yellow-fill
  placeholder and "Not disclosed in OM" as the source — don't model a guessed fee and don't
  silently drop the class from the workbook.

## Tab 6: Sensitivity (only if the OM provides sensitivity/scenario tables)
- Rebuild the OM's own sensitivity matrices (e.g. return vs. exit cap rate, return vs. rent
  growth) as live data tables or a small formula grid driven off Tab 2 — not a static screenshot
  or a copy of the OM's numbers. If the workbook's own IRR formula (Tab 5) doesn't reproduce the
  OM's base case exactly, the sensitivity grid should be built off the workbook's own formula
  chain (consistent with the rest of the model) and the memo should note the base-case variance
  once, rather than the grid silently disagreeing with Tab 5.
- Skip this tab entirely if the OM gives no sensitivity data — don't invent scenarios.

## General
- Freeze header rows/columns for readability
- Number formats per xlsx skill conventions: currency `$#,##0`, percentages `0.0%` stored as
  fractions, multiples `0.0x`
- Recalculate with recalc.py before delivery — zero formula errors required
