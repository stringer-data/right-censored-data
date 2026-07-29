# Right-Censored Data: Case Studies

A learning project working through right-censored data and survival analysis via six case studies, roughly ordered from foundational to advanced. Two are product-analytics flavored (churn, conversion), one is trust & safety (fraud), and three are the "classic" domains where survival analysis was born (reliability engineering, clinical trials) plus a hybrid (LTV).

## What is right-censoring?

An observation is right-censored when we know the event of interest *hasn't happened yet* by the end of our observation window, but we don't know if/when it will. A user who's still subscribed at the end of your dataset, a machine still running, a patient still alive at study end — all right-censored. Treating these as "no event" (or dropping them) biases every downstream estimate. Survival analysis exists to handle this correctly.

## Case studies

| # | Project | Domain | Core technique |
|---|---------|--------|-----------------|
| 01 | [subscription-churn-km-coxph](./01-subscription-churn-km-coxph) | Product analytics | Kaplan-Meier curves, log-rank test, Cox proportional hazards |
| 02 | [trial-to-paid-conversion](./02-trial-to-paid-conversion) | Product analytics | Time-to-event with censoring, parametric AFT models |
| 03 | [customer-ltv-under-censoring](./03-customer-ltv-under-censoring) | Product analytics / general | Restricted mean survival time, naive-vs-correct LTV estimation |
| 04 | [equipment-reliability-weibull](./04-equipment-reliability-weibull) | Reliability engineering | Weibull fitting, hazard functions, MTTF |
| 05 | [clinical-trial-survival](./05-clinical-trial-survival) | Biostatistics | Kaplan-Meier, log-rank test, Cox PH (the textbook case study) |
| 06 | [fraud-chargeback-censoring](./06-fraud-chargeback-censoring) | Trust & safety / payments risk | Real data (IEEE-CIS) + synthetic reporting-lag censoring, KM, AFT models |

Work through them in order if you want KM → Cox → parametric → applied, or jump straight to whichever domain is most relevant to you. Each project folder has its own README with background, dataset notes, and a set of questions to answer — the same shape a real case study writeup would take.

## Stack

Python, primarily [lifelines](https://lifelines.readthedocs.io/) for KM/Cox/parametric models, `scikit-survival` where a project calls for ML-flavored survival models, plus the usual pandas/numpy/matplotlib.

```
pip install -r requirements.txt
```

## Workflow

Each project folder is self-contained: a `README.md` with the brief, a `data/` folder (either a small dataset or a script to generate synthetic data), and a `notebooks/` folder where you do the actual analysis. Work through a project, then commit and push it before moving to the next.
