# 06 — Fraud Chargeback Reporting Under Censoring

**Domain:** Trust & safety / payments risk
**Core techniques:** Time-to-event framing of a delayed label, Kaplan-Meier, parametric AFT models, real-world data with a synthetic censoring layer

## The setup

A transaction isn't labeled fraudulent the moment it happens -- it's labeled fraudulent once a cardholder disputes it and a chargeback is reported, which can take anywhere from days to months. If you compute "fraud rate" as `reported_fraud / total transactions` at some snapshot in time, you systematically understate it, and you understate it *more* for transactions that happened recently, because they've had less time for a chargeback to surface. This is the same cohort-maturity bias as [02](../02-trial-to-paid-conversion), applied to a real dataset instead of a fully synthetic one.

This project uses real transaction data (Kaggle's IEEE-CIS Fraud Detection competition) with a synthetic reporting-lag / censoring layer built on top, since the real dataset ships fully-resolved labels that a real fraud team would never have at decision time.

## Data

1. Join the [IEEE-CIS Fraud Detection](https://www.kaggle.com/competitions/ieee-fraud-detection) competition on Kaggle and download `train_transaction.csv`.
2. Place it at `data/raw/train_transaction.csv` (gitignored -- it's ~680MB and isn't committed to this repo).
3. Run `python data/prepare_data.py`. It subsamples ~40k transactions, treats the real `isFraud` label as latent ground truth, simulates a chargeback-reporting delay (lognormal, long right tail) for the truly-fraudulent transactions, and applies an observation cutoff (`observed_through_date`). Writes `data/fraud_censored.csv`.

Resulting columns:
- `transaction_id`, `transaction_date`, `observed_through_date`
- `transaction_amt`, `product_cd`, `card_type`, `card_category`
- `days_to_report_or_censoring` — days from transaction to whichever happened first: chargeback reported, or the observation cutoff
- `reported_fraud` — 1 if a chargeback had actually been reported by the cutoff, 0 if censored (includes both "genuinely not fraud" and "fraud, but not yet reported" — you can't tell these apart from the observed data alone, same as real fraud ops)
- `_true_is_fraud` — the real Kaggle ground-truth label. This is your answer key for checking recovered estimates at the end; don't use it as a model feature, and don't peek before you've done the KM/AFT work.

You'll need to derive days-since-transaction / cohort age yourself from `transaction_date` and `observed_through_date`, same as project 02.

## Questions to work through

1. Compute the naive reported-fraud rate (`reported_fraud.mean()`) overall and by weekly transaction cohort. Show how it's biased downward for recent cohorts, and compare the overall naive rate against `_true_is_fraud.mean()` to see the size of the gap.
2. Fit a Kaplan-Meier curve for "time to chargeback report" and use it to project the *eventual* reported-fraud rate, correcting for censoring. How much closer does that get you to the true rate from Q1?
3. Fit a Weibull AFT (or log-normal AFT) model on `days_to_report_or_censoring`. What does the fitted shape imply about how chargeback-reporting hazard changes over time — are most disputes reported early, or is there a long tail?
4. Does `transaction_amt` or `product_cd` shift the reporting-time distribution (i.e., do larger transactions get disputed faster)? Quantify with the AFT model's covariate effect.
5. Pick an operational cutoff (e.g. "transactions from the last 14 days") and answer: "Of the transactions in this window not yet flagged, what fraction do we expect to eventually turn out fraudulent?" — this is the number a real fraud team needs for staffing/reserve decisions, and it's exactly the kind of conditional-survival question naive labeling can't answer.
6. Only after finishing 1-5: compare your KM-corrected and AFT-projected fraud rate estimates against `_true_is_fraud`. How close did you get, and where did the estimate still fall short (e.g. does the lognormal tail assumption undershoot vs. what actually happened)?

## Suggested tools

`lifelines.KaplanMeierFitter`, `lifelines.WeibullAFTFitter`, `lifelines.LogNormalAFTFitter`, conditional survival via `.predict()` / `.survival_function_at_times()`
