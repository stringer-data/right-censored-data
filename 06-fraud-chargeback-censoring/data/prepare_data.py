"""
Builds the fraud-chargeback censoring dataset from the real IEEE-CIS Fraud
Detection transaction data, with a synthetic chargeback-reporting-lag layer
added on top.

Why a synthetic layer on real data: IEEE-CIS ships a fully-resolved isFraud
label for every row (Kaggle needed clean ground truth for scoring). Real
fraud ops teams don't get that -- a transaction is only labeled fraudulent
once a chargeback/dispute is *reported*, and reporting lags the transaction
by anywhere from days to months. This script treats isFraud as latent ground
truth (like the true, unobservable event time in a survival problem) and
simulates the reporting-lag process on top of it, then applies an
observation cutoff (snapshot_date) to produce what would actually have been
knowable at that point in time -- some genuinely-fraudulent transactions
haven't been reported yet as of the cutoff, i.e. they're right-censored.

Setup (one-time, not run by this script):
  1. Join the IEEE-CIS Fraud Detection competition on Kaggle:
     https://www.kaggle.com/competitions/ieee-fraud-detection
  2. Download train_transaction.csv (the identity file isn't needed here)
  3. Place it at data/raw/train_transaction.csv (gitignored -- ~680MB, not
     committed to this repo)

Run: python prepare_data.py
Reads:  raw/train_transaction.csv
Writes: fraud_censored.csv, _construction_notes.md
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

RAW_PATH = "raw/train_transaction.csv"
OUT_PATH = "fraud_censored.csv"
N_SAMPLE = 40_000  # subsample for a case-study-sized dataset

# TransactionDT is seconds elapsed from an arbitrary reference point (not a
# real calendar date). Common convention in public IEEE-CIS work is to treat
# it as starting 2017-12-01; we do the same purely for readable dates.
REFERENCE_DATE = pd.Timestamp("2017-12-01")

# Reporting-lag distribution for transactions that ARE truly fraudulent
# (isFraud == 1). Lognormal: most chargebacks land around ~3-4 weeks, with a
# long right tail out to several months -- matches how card networks
# describe chargeback timing (cardholders often have 60-120 days to dispute).
LAG_MEDIAN_DAYS = 25.0
LAG_SIGMA = 0.9  # lognormal shape: controls the long tail

# Observation cutoff: the "today" of this dataset. Transactions near the
# cutoff haven't had time for their chargeback to be reported yet, even if
# genuinely fraudulent -- this is what creates the censoring.
SNAPSHOT_LOOKBACK_DAYS = 120  # snapshot_date = latest transaction date - this


def main():
    raw = pd.read_csv(RAW_PATH)

    df = raw.sample(n=min(N_SAMPLE, len(raw)), random_state=42).reset_index(drop=True)

    df["transaction_date"] = REFERENCE_DATE + pd.to_timedelta(df["TransactionDT"], unit="s")

    snapshot_date = df["transaction_date"].max() - pd.Timedelta(days=SNAPSHOT_LOOKBACK_DAYS)

    n = len(df)
    is_fraud = df["isFraud"] == 1

    # Latent reporting delay for the fraudulent transactions -- unobservable
    # in real life; here it's simulated so we can later check recovery.
    u = RNG.random(n)
    true_reporting_delay_days = LAG_MEDIAN_DAYS * np.exp(LAG_SIGMA * _norm_ppf(u))

    days_since_transaction_at_snapshot = (snapshot_date - df["transaction_date"]).dt.days.clip(lower=0)

    # A transaction can only be labeled fraud in the *observed* data if it is
    # truly fraudulent AND its chargeback has been reported by the snapshot.
    reported_by_snapshot = is_fraud & (true_reporting_delay_days <= days_since_transaction_at_snapshot)

    # time_to_report_or_censoring: days from transaction to whichever
    # happened first among chargeback report or the observation cutoff.
    # Genuine transactions never have a true event, so their "time" is
    # simply how long they've been observed -- always censored.
    time_to_report_or_censoring = np.where(
        is_fraud,
        np.minimum(true_reporting_delay_days, days_since_transaction_at_snapshot),
        days_since_transaction_at_snapshot,
    )

    out = pd.DataFrame(
        {
            "transaction_id": df["TransactionID"],
            "transaction_date": df["transaction_date"].dt.strftime("%Y-%m-%d"),
            "observed_through_date": snapshot_date.strftime("%Y-%m-%d"),
            "transaction_amt": df["TransactionAmt"],
            "product_cd": df["ProductCD"],
            "card_type": df.get("card4"),
            "card_category": df.get("card6"),
            "days_to_report_or_censoring": np.round(time_to_report_or_censoring, 1),
            "reported_fraud": reported_by_snapshot.astype(int),
            # True label, kept for grading your own recovered estimates
            # against reality -- don't use this as a model feature.
            "_true_is_fraud": df["isFraud"],
        }
    )

    out.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} with {len(out)} rows")
    print(f"Naive reported-fraud rate at snapshot: {out['reported_fraud'].mean():.4f}")
    print(f"True underlying fraud rate (hidden in real deployment): {out['_true_is_fraud'].mean():.4f}")

    with open("_construction_notes.md", "w") as f:
        f.write(
            "# Construction notes (don't peek until you've done the analysis)\n\n"
            "- Base data: IEEE-CIS Fraud Detection train_transaction.csv, "
            f"{N_SAMPLE}-row subsample. `_true_is_fraud` is the real Kaggle label.\n"
            f"- Reporting delay for truly-fraudulent transactions: lognormal, "
            f"median {LAG_MEDIAN_DAYS} days, sigma {LAG_SIGMA} (long right tail -- "
            "some chargebacks take months to surface).\n"
            f"- Genuine (non-fraud) transactions never generate a chargeback -- they "
            "are always censored at the observation cutoff, same as an active "
            "subscriber who hasn't churned.\n"
            f"- snapshot_date = latest transaction date minus {SNAPSHOT_LOOKBACK_DAYS} days, "
            "so a meaningful chunk of recent transactions are still censored purely "
            "because not enough time has passed for a chargeback to land, not because "
            "they aren't fraudulent. This is what makes reported_fraud.mean() an "
            "understatement of the true fraud rate, worse for more recent cohorts.\n"
            "- `_true_is_fraud` is included only so you can check your KM/AFT-recovered "
            "estimates against reality afterward -- treat it as answer-key, not a feature.\n"
        )


def _norm_ppf(u):
    # Inverse CDF of the standard normal via erfinv, avoids a scipy dependency.
    from scipy.special import erfinv

    return np.sqrt(2) * erfinv(2 * u - 1)


if __name__ == "__main__":
    main()
