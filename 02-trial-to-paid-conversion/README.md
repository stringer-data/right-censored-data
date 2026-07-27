# 02 — Trial-to-Paid Conversion Under Censoring

**Domain:** Product analytics (freemium/trial funnels)
**Core techniques:** Time-to-event framing of a conversion funnel, parametric AFT models (Weibull, log-normal), model comparison

## The setup

Users start a 30-day free trial. The "event" is converting to paid. At any snapshot in time, some users have converted, some have explicitly churned out of the trial, and some are still mid-trial — that last group is right-censored. Product teams often report conversion rate as `converted / total signups`, which is wrong while cohorts are still maturing (it understates true eventual conversion for cohorts that haven't finished their window). This project is about doing it properly.

## Data

Generate synthetic trial data (script in `data/`) with:
- `signup_date` — when the user started their trial
- `observed_through_date` — the data-pull cutoff; everyone's observation window ends here at the latest
- `days_to_conversion_or_censoring` — days from signup to whichever happened first: conversion, explicit trial-cancel, or the observation cutoff
- `converted` — 1 if conversion was actually observed, 0 if censored (includes both "still in trial" and "explicitly canceled" — decide how you want to treat cancellation, and justify it)
- `onboarding_completed` — bool, whether user finished onboarding flow
- `signup_source`

You'll need to derive days-since-signup / cohort age yourself from `signup_date` and `observed_through_date` — it isn't handed to you as a precomputed column, same as it wouldn't be in real product data.

## Questions to work through

1. Compute naive conversion rate (`converted / total`) per weekly cohort and show how it's biased downward for immature cohorts.
2. Fit Kaplan-Meier per cohort and compare the *projected eventual* conversion rate against the naive one.
3. Fit both a Weibull AFT and a log-normal AFT model on time-to-conversion. Which fits better (AIC/BIC)? What does each imply about how conversion hazard changes over the trial window (increasing/decreasing/constant)?
4. Use the fitted model to answer: "Of users still in-trial at day 10 who haven't converted, what's the probability they convert by day 30?" (conditional survival)
5. Does `onboarding_completed` shift the conversion-time distribution? Quantify with the AFT model's covariate effect (accelerates or decelerates time-to-event).

## Suggested tools

`lifelines.WeibullAFTFitter`, `lifelines.LogNormalAFTFitter`, `lifelines.KaplanMeierFitter`, conditional survival via `.predict()` / `.survival_function_at_times()`
