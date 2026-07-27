# Ground truth (don't peek until you've done the analysis)

- Baseline time-to-convert: Weibull(shape=1.8, scale=20.0 days)
  -> shape > 1 means increasing hazard: conversion becomes MORE likely
  per unit time as users approach the trial deadline, not less.
- onboarding_completed AFT factor: 0.6 (factor < 1 means it SPEEDS UP conversion; multiplies the time-to-event)
- signup_source AFT factors: {'organic': 1.25, 'paid': 1.0, 'referral': 0.75, 'partner': 0.8}
- 25% of users who would not have converted within the 30-day trial explicitly cancel early instead of silently running out the clock -- treated as censoring in this dataset.
- Trial length: 30 days. Signups staggered over the last 84 days before the snapshot date, which is what makes recent cohorts look artificially low-converting if you compute naive conversion rate without accounting for censoring.
