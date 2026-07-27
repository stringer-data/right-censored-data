# 04 — Equipment Reliability: Weibull Analysis

**Domain:** Reliability engineering (the classic origin domain of survival analysis)
**Core techniques:** Weibull distribution fitting, hazard function shape, Mean Time To Failure (MTTF), bathtub curve intuition

## The setup

A fleet of machines (servers, industrial equipment, appliances — pick a flavor) is under test/observation. Some units fail during the observation window (event observed), others are still running when the study ends or are pulled from the test early (right-censored, sometimes called "suspended" in reliability terminology). The goal is to characterize the failure-time distribution well enough to answer: when should we schedule preventive maintenance, and what's the expected warranty cost?

This is the domain reliability engineers have used survival analysis (there called "reliability analysis") in for decades, and it's where a lot of the vocabulary (hazard rate, bathtub curve, MTTF) originates — useful to see it in its native habitat before mapping it back to product/business use.

## Data

Generate synthetic failure-time data (script in `data/`) for ~500–1,000 units:
- `hours_to_event` — operating hours until failure or censoring
- `failed` — 1 if failure observed, 0 if censored (still running, or removed from test)
- `unit_type` or `manufacturing_batch` — categorical, with a deliberate reliability difference between groups
- `stress_level` — e.g. an operating-condition covariate (temperature/load) that accelerates failure

Simulate at least one batch with a Weibull shape parameter < 1 (infant mortality / decreasing hazard) and one with shape > 1 (wear-out / increasing hazard), so the case study has something interesting to distinguish.

## Questions to work through

1. Fit a Weibull distribution to the full pooled dataset. Report the shape (k) and scale (λ) parameters — is the estimated hazard increasing, decreasing, or constant over time?
2. Fit separately by `unit_type`/batch. Which batch shows infant-mortality failures vs. wear-out failures? How would maintenance policy differ for each?
3. Compute MTTF (mean time to failure) from the fitted Weibull, and compare it to the naive mean of `hours_to_event` ignoring censoring — quantify the underestimate.
4. Fit a Weibull AFT model with `stress_level` as a covariate. How much does the acceleration factor change expected lifetime?
5. Using the fitted model, compute at what operating hour cumulative failure probability first exceeds 10% — a natural preventive-maintenance trigger point.

## Suggested tools

`lifelines.WeibullFitter`, `lifelines.WeibullAFTFitter`, `scipy.stats.weibull_min` for cross-checking
