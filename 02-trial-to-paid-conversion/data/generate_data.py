"""
Generates a synthetic trial-to-paid conversion dataset with right-censoring.

Ground truth (kept out of the CSV, written to _ground_truth.md instead so it
doesn't spoil the analysis):
  - baseline time-to-convert ~ Weibull(shape=1.8, scale=20 days)
    -> increasing hazard as the 30-day trial deadline approaches
  - onboarding_completed accelerates conversion (AFT factor 0.6)
  - signup_source shifts conversion speed (referral/partner faster, organic slower)
  - 25% of users who don't convert explicitly cancel their trial early
    (treated as censoring here -- see README for the competing-risks discussion)
  - signups are staggered over the last 84 days before the snapshot date, so
    recent cohorts are censored by the snapshot itself, not just the 30-day
    trial window -- this is what creates the cohort-maturity bias in Q1.

Run: python generate_data.py
Writes: trial_conversion.csv
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N = 3000
TRIAL_LENGTH_DAYS = 30
LOOKBACK_DAYS = 84  # snapshot pulled "today"; signups happened up to 84 days ago
SNAPSHOT_DATE = pd.Timestamp("2024-06-01")

BASELINE_SHAPE = 1.8
BASELINE_SCALE = 20.0

SOURCE_LEVELS = ["organic", "paid", "referral", "partner"]
SOURCE_PROBS = [0.45, 0.30, 0.15, 0.10]
SOURCE_AFT_FACTOR = {"organic": 1.25, "paid": 1.0, "referral": 0.75, "partner": 0.80}

ONBOARDING_COMPLETE_RATE = 0.55
ONBOARDING_AFT_FACTOR = 0.6  # completing onboarding accelerates conversion

EXPLICIT_CANCEL_RATE_AMONG_NONCONVERTERS = 0.25


def main():
    user_id = np.arange(1, N + 1)
    signup_source = RNG.choice(SOURCE_LEVELS, size=N, p=SOURCE_PROBS)
    onboarding_completed = RNG.random(N) < ONBOARDING_COMPLETE_RATE

    days_since_signup_at_snapshot = RNG.uniform(0, LOOKBACK_DAYS, size=N).astype(int)
    signup_date = SNAPSHOT_DATE - pd.to_timedelta(days_since_signup_at_snapshot, unit="D")

    aft_factor = np.array([SOURCE_AFT_FACTOR[s] for s in signup_source])
    aft_factor = aft_factor * np.where(onboarding_completed, ONBOARDING_AFT_FACTOR, 1.0)

    # Weibull AFT: true_time = scale * factor * (-ln(U))^(1/shape)
    u = RNG.random(N)
    true_time_to_convert = BASELINE_SCALE * aft_factor * (-np.log(u)) ** (1 / BASELINE_SHAPE)

    # Explicit early trial cancellation for a subset of would-be non-converters
    would_convert_in_trial = true_time_to_convert <= TRIAL_LENGTH_DAYS
    explicit_cancel = (~would_convert_in_trial) & (
        RNG.random(N) < EXPLICIT_CANCEL_RATE_AMONG_NONCONVERTERS
    )
    cancel_day = RNG.uniform(5, TRIAL_LENGTH_DAYS - 1, size=N)

    # Observation horizon: capped by trial length AND by how long the user has
    # actually been observed as of the snapshot date.
    observation_cap = np.minimum(TRIAL_LENGTH_DAYS, days_since_signup_at_snapshot)

    # days_to_conversion_or_censoring: days from signup to whichever happened
    # first among conversion, explicit cancellation, or the observation cutoff.
    time_to_event_days = np.minimum(true_time_to_convert, observation_cap)
    # converted: 1 if conversion was actually observed by the cutoff, 0 if the
    # user was still unconverted (censored) as of that cutoff.
    event_observed = (true_time_to_convert <= observation_cap).astype(int)

    # Apply explicit cancellation: if it happens before the observation cap
    # and before conversion, it censors the observation at the cancel day.
    cancels_before_cap = explicit_cancel & (cancel_day < observation_cap)
    time_to_event_days = np.where(
        cancels_before_cap & (event_observed == 0),
        np.minimum(cancel_day, observation_cap),
        time_to_event_days,
    )

    df = pd.DataFrame(
        {
            "user_id": user_id,
            "signup_date": signup_date.strftime("%Y-%m-%d"),
            "signup_source": signup_source,
            "onboarding_completed": onboarding_completed,
            "observed_through_date": SNAPSHOT_DATE.strftime("%Y-%m-%d"),
            "days_to_conversion_or_censoring": np.round(time_to_event_days, 1),
            "converted": event_observed,
        }
    )

    df.to_csv("trial_conversion.csv", index=False)
    print(f"Wrote trial_conversion.csv with {len(df)} rows")
    print(f"Overall conversion rate (naive): {df['converted'].mean():.3f}")

    with open("_ground_truth.md", "w") as f:
        f.write(
            "# Ground truth (don't peek until you've done the analysis)\n\n"
            f"- Baseline time-to-convert: Weibull(shape={BASELINE_SHAPE}, scale={BASELINE_SCALE} days)\n"
            f"  -> shape > 1 means increasing hazard: conversion becomes MORE likely\n"
            "  per unit time as users approach the trial deadline, not less.\n"
            f"- onboarding_completed AFT factor: {ONBOARDING_AFT_FACTOR} "
            "(factor < 1 means it SPEEDS UP conversion; multiplies the time-to-event)\n"
            f"- signup_source AFT factors: {SOURCE_AFT_FACTOR}\n"
            f"- {EXPLICIT_CANCEL_RATE_AMONG_NONCONVERTERS:.0%} of users who would not have "
            "converted within the 30-day trial explicitly cancel early instead of "
            "silently running out the clock -- treated as censoring in this dataset.\n"
            "- Trial length: 30 days. Signups staggered over the last 84 days before "
            "the snapshot date, which is what makes recent cohorts look artificially "
            "low-converting if you compute naive conversion rate without accounting "
            "for censoring.\n"
        )


if __name__ == "__main__":
    main()
