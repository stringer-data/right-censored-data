# Construction notes (don't peek until you've done the analysis)

- Base data: IEEE-CIS Fraud Detection train_transaction.csv, 40000-row subsample. `_true_is_fraud` is the real Kaggle label.
- Reporting delay for truly-fraudulent transactions: lognormal, median 25.0 days, sigma 0.9 (long right tail -- some chargebacks take months to surface).
- Genuine (non-fraud) transactions never generate a chargeback -- they are always censored at the observation cutoff, same as an active subscriber who hasn't churned.
- snapshot_date = latest transaction date minus 45 days, so a meaningful chunk of recent transactions are still censored purely because not enough time has passed for a chargeback to land, not because they aren't fraudulent. This is what makes reported_fraud.mean() an understatement of the true fraud rate, worse for more recent cohorts.
- `_true_is_fraud` is included only so you can check your KM/AFT-recovered estimates against reality afterward -- treat it as answer-key, not a feature.
