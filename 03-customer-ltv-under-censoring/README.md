# 03 — Customer LTV Under Censoring

**Domain:** Product analytics / general
**Core techniques:** Restricted mean survival time (RMST), naive vs. survival-corrected LTV, sensitivity to horizon choice

## The setup

"What's our average customer lifetime value?" is one of the most common — and most often mis-computed — product analytics questions. If a chunk of your customer base is still active, you either drop them (biases toward short-lived customers) or you use their current tenure as their final tenure (biases toward the current moment, understating true lifetime). This project builds the correct estimator and shows exactly how wrong the shortcuts are, using dollar amounts instead of just tenure so the stakes are concrete.

## Data

Reuse or extend the churn dataset style from project 01, but add revenue:
- `tenure_days`, `churned` (censoring indicator) — as before
- `monthly_revenue` per subscriber (varies by plan)
- Compute `revenue_to_date` as a derived column

You want a mix of long-tenured active accounts (heavily censored) and a realistic churn curve.

## Questions to work through

1. Compute "naive LTV" three ways: (a) revenue-to-date averaged over all customers, (b) revenue-to-date averaged over churned-only customers, (c) projected using average tenure × average monthly revenue. Show how differently these disagree.
2. Compute Restricted Mean Survival Time (RMST) at a chosen horizon (e.g. 365 days) from the KM curve, and convert to expected revenue over that horizon. This is your "correct" LTV-to-horizon estimate.
3. Sensitivity check: how much does the RMST-based LTV estimate change as you vary the horizon (90 / 180 / 365 / 730 days)? Why does horizon choice matter so much whenever a survival curve hasn't fully decayed to zero within your window?
4. Segment RMST-based LTV by plan and acquisition channel — which segment is actually most valuable once you correct for censoring, versus what the naive numbers suggested?
5. Write up, in plain language, why RMST is the "expected value of the minimum of survival time and horizon" and why that's the right quantity for a bounded LTV estimate (full unbounded expected lifetime is often not identifiable from finite follow-up data).

## Suggested tools

`lifelines.KaplanMeierFitter` (`.rmst()` / manual integration of the survival function), pandas for the naive comparisons
