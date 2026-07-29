# Ground truth (don't peek until you've done the analysis)

- Baseline time-to-churn: Weibull(shape=1.3, scale=380.0 days)
  -> shape > 1 means mildly increasing hazard over time.
- plan AFT factors: {'basic': 1.0, 'pro': 1.4, 'enterprise': 2.2} (factor > 1 SLOWS churn; multiplies time-to-event)
- acquisition_channel AFT factors: {'organic': 1.0, 'paid': 0.7, 'referral': 1.3} (factor > 1 SLOWS churn)
- Signups staggered over the 24 months before the window close date (2024-06-01), so recent cohorts are heavily censored -- this is what creates the bias in the naive 'average tenure of churned-only users' estimate in Q5.
