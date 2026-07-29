"""
Generates a synthetic SaaS subscription-churn dataset with right-censoring.

Ground truth (kept out of the CSV, written to _ground_truth.md instead so it
doesn't spoil the analysis):
  - baseline time-to-churn ~ Weibull(shape=1.3, scale=380 days)
    -> mildly increasing hazard (subscribers get slightly more likely to
    churn the longer they stick around, not less)
  - plan shifts churn speed (enterprise slowest, basic fastest)
  - acquisition_channel shifts churn speed (paid fastest, referral slowest)
  - signups are staggered over the 24 months before the observation window
    closes, so recent cohorts are heavily censored (still active, not yet
    given the chance to churn) while old cohorts are mostly resolved

Run: python generate_data.py
Writes: subscription_churn.csv
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N = 4000
WINDOW_CLOSE_DATE = pd.Timestamp("2024-06-01")
LOOKBACK_MONTHS = 24

BASELINE_SHAPE = 1.3
BASELINE_SCALE = 380.0  # days

PLAN_LEVELS = ["basic", "pro", "enterprise"]
PLAN_PROBS = [0.55, 0.32, 0.13]
PLAN_AFT_FACTOR = {"basic": 1.0, "pro": 1.4, "enterprise": 2.2}  # >1 slows churn

CHANNEL_LEVELS = ["organic", "paid", "referral"]
CHANNEL_PROBS = [0.45, 0.35, 0.20]
CHANNEL_AFT_FACTOR = {"organic": 1.0, "paid": 0.7, "referral": 1.3}  # >1 slows churn


def main():
    subscriber_id = np.arange(1, N + 1)
    plan = RNG.choice(PLAN_LEVELS, size=N, p=PLAN_PROBS)
    acquisition_channel = RNG.choice(CHANNEL_LEVELS, size=N, p=CHANNEL_PROBS)

    days_since_signup_at_close = RNG.uniform(0, LOOKBACK_MONTHS * 30, size=N).astype(int)
    signup_date = WINDOW_CLOSE_DATE - pd.to_timedelta(days_since_signup_at_close, unit="D")
    signup_cohort_month = signup_date.to_period("M").astype(str)

    aft_factor = np.array([PLAN_AFT_FACTOR[p] for p in plan]) * np.array(
        [CHANNEL_AFT_FACTOR[c] for c in acquisition_channel]
    )

    # Weibull AFT: true_time = scale * factor * (-ln(U))^(1/shape)
    u = RNG.random(N)
    true_time_to_churn = BASELINE_SCALE * aft_factor * (-np.log(u)) ** (1 / BASELINE_SHAPE)

    # Observed tenure is capped by how long we've actually had the chance to
    # watch this subscriber, i.e. by the observation window close.
    tenure_days = np.minimum(true_time_to_churn, days_since_signup_at_close)
    churned = (true_time_to_churn <= days_since_signup_at_close).astype(int)

    df = pd.DataFrame(
        {
            "subscriber_id": subscriber_id,
            "signup_cohort_month": signup_cohort_month,
            "plan": plan,
            "acquisition_channel": acquisition_channel,
            "tenure_days": np.round(tenure_days, 1),
            "churned": churned,
        }
    )

    df.to_csv("subscription_churn.csv", index=False)
    print(f"Wrote subscription_churn.csv with {len(df)} rows")
    print(f"Overall churn rate (naive, observed-so-far): {df['churned'].mean():.3f}")

    with open("_ground_truth.md", "w") as f:
        f.write(
            "# Ground truth (don't peek until you've done the analysis)\n\n"
            f"- Baseline time-to-churn: Weibull(shape={BASELINE_SHAPE}, scale={BASELINE_SCALE} days)\n"
            "  -> shape > 1 means mildly increasing hazard over time.\n"
            f"- plan AFT factors: {PLAN_AFT_FACTOR} (factor > 1 SLOWS churn; multiplies time-to-event)\n"
            f"- acquisition_channel AFT factors: {CHANNEL_AFT_FACTOR} (factor > 1 SLOWS churn)\n"
            f"- Signups staggered over the {LOOKBACK_MONTHS} months before the window close date "
            f"({WINDOW_CLOSE_DATE.date()}), so recent cohorts are heavily censored -- "
            "this is what creates the bias in the naive 'average tenure of churned-only "
            "users' estimate in Q5.\n"
        )


if __name__ == "__main__":
    main()
