# 05 — Clinical Trial Survival Analysis (the textbook case study)

**Domain:** Biostatistics / clinical trials
**Core techniques:** Kaplan-Meier, log-rank test, Cox proportional hazards — the canonical trio, on a canonical dataset

## The setup

This is deliberately the "textbook" case study: survival analysis exists largely because of trials like this one, where patients are followed for a fixed study period, some die/relapse (event), and others survive to the end of the study or drop out (right-censored). Working this dataset is the fastest way to build the reference mental model you'll then recognize everywhere else (churn, reliability, etc. are all structurally the same problem).

Unlike the other projects, use a **real, well-known public dataset** here rather than synthetic data — it's small, well-documented, and widely used in survival-analysis teaching material, so you can sanity-check your results against known published figures.

## Data

Use a built-in dataset from `lifelines` — no download needed:

```python
from lifelines.datasets import load_lung  # or load_rossi, load_gbsg2
df = load_lung()
```

`load_lung()` (NCCTG lung cancer data) is a good default: `time` (days), `status` (censoring indicator), plus covariates like `age`, `sex`, `ph.ecog` (performance status). Read the docstring / lifelines docs for the exact column encoding before starting (status is coded 1=censored, 2=dead — not the usual 0/1).

## Questions to work through

1. Plot the overall Kaplan-Meier survival curve with confidence intervals. What's the median survival time?
2. Stratify by `sex`. Plot both KM curves on one axes and run a log-rank test — is the survival difference between sexes significant?
3. Fit a Cox proportional hazards model with `age`, `sex`, `ph.ecog` as covariates. Interpret each hazard ratio in plain language.
4. Check the proportional hazards assumption for each covariate (Schoenfeld residuals via `check_assumptions`). Does everything hold up?
5. Pick one covariate and produce adjusted survival curves at a few representative values (e.g. predicted survival curve for a 60-year-old vs. a 75-year-old, holding other covariates fixed) — this is the step that turns a Cox model from "significant coefficient" into an actual, communicable prediction.

## Suggested tools

`lifelines.datasets.load_lung`, `lifelines.KaplanMeierFitter`, `lifelines.CoxPHFitter`, `lifelines.statistics.logrank_test`
