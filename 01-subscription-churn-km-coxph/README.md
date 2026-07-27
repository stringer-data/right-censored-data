# 01 — Subscription Churn: Kaplan-Meier & Cox Proportional Hazards

**Domain:** Product analytics (SaaS subscriptions)
**Core techniques:** Kaplan-Meier estimator, log-rank test, Cox proportional hazards regression

## The setup

You have a SaaS product with monthly subscriptions. You're asked: "What's the median subscriber lifetime, and which plan/acquisition-channel combos churn fastest?" Your dataset covers a fixed observation window, so a meaningful chunk of subscribers are still active at the end of it — right-censored. If you just filter to "subscribers who churned" and average their tenure, you'll systematically underestimate lifetime (you're excluding your longest-lived, still-active customers).

## Data

Generate a synthetic dataset (a script belongs in `data/`) of ~2,000–5,000 subscribers with:
- `tenure_days` — days observed (from signup to churn or to end-of-window)
- `churned` — 1 if churn observed, 0 if censored (still active at window close)
- `plan` — e.g. basic / pro / enterprise
- `acquisition_channel` — e.g. organic / paid / referral
- `signup_cohort_month`

Build in a real effect (e.g. enterprise churns slower, paid-channel users churn faster) so your models have something true to recover.

## Questions to work through

1. Plot overall Kaplan-Meier survival curve. What's the median subscriber lifetime (with confidence interval)?
2. Stratify KM curves by `plan`. Are the differences statistically significant (log-rank test)?
3. Fit a Cox proportional hazards model with `plan`, `acquisition_channel`, `signup_cohort_month` as covariates. Interpret the hazard ratios.
4. Check the proportional hazards assumption (e.g. `check_assumptions` in lifelines). What do you do if it's violated?
5. Compare your KM-based median lifetime estimate against the naive "average tenure of churned users only" — quantify the bias.

## Suggested tools

`lifelines.KaplanMeierFitter`, `lifelines.CoxPHFitter`, `lifelines.statistics.logrank_test`
