# Interrupted Time Series Analysis: Transit Ridership Impact Study

**Author:** Tomasz Solis  
**Date:** December 2025  
**Objective:** Rigorous ITS methodology practice using synthetic transit data

---

## Project Overview

This project applies Interrupted Time Series (ITS) analysis to measure the causal impact of express bus lanes on transit ridership. The analysis uses synthetic weekly ridership data spanning 2020-2024, with the intervention occurring January 1, 2024.

**Why this project exists:**  
ITS is a powerful quasi-experimental method for policy evaluation when randomized experiments aren't feasible. This project serves as methodological practice for applying ITS to real-world business analytics challenges involving big-bang rollouts, multiple segments, and messy observational data.

---

## The Research Question

**Did dedicated express bus lanes increase transit ridership?**

Metropolitan Transit Authority launched express bus lanes across the city on January 1, 2024. All routes were affected simultaneously (no control group), making this a natural candidate for ITS analysis.

**Key challenges:**
- Multiple route types with different baseline dynamics
- Seasonal patterns in ridership
- Concurrent events near intervention date
- Non-parallel pre-intervention trends across segments

These mirror real-world complications in policy evaluation and product analytics.

---

## Dataset Structure

**Current dataset:** Baseline (easy mode)  
- 783 observations (261 weeks × 3 route types)
- January 2020 - December 2024
- Route types: Downtown, Suburban, Cross-town
- Known treatment effects for validation

**Future dataset:** Realistic (hard mode)  
- Same structure, but with smaller effects, more noise, and ambiguous results
- Tests methodology under realistic conditions

---

## Repository Structure

```
transit-its-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── easy_mode/
│   │   └── transit_ridership_baseline.csv
│   └── hard_mode/
│       └── (coming later)
├── notebooks/
│   ├── 01_eda_baseline.ipynb           # Current: EDA and assumption testing
│   └── 02_its_model_baseline.ipynb     # TBD
├── outputs/
│   ├── figures/                         # Generated plots
│   └── results/                         # Model outputs and tables
└── src/
    └── (utility functions as needed)
```

---

## Current Progress

### ✅ Completed: Exploratory Data Analysis

**Notebook:** `01_eda_baseline.ipynb`

**Key findings:**

1. **Data Quality:** Complete dataset, no missing values, consistent 7-day intervals

2. **Pre-Intervention Trends:** NOT parallel across route types
   - Downtown: 2.45 riders/week growth
   - Suburban: 1.67 riders/week growth
   - Cross-town: 1.09 riders/week growth
   - Downtown growing 2.25x faster than Cross-town (125% difference)

3. **Seasonality:** Significant in 2 of 3 route types (p < 0.05)
   - Requires month fixed effects in models

4. **Visual Evidence:** Clear level increase at January 2024 across all routes

5. **Autocorrelation:** Likely present (weekly time series)
   - Will require Newey-West robust standard errors

**Critical methodological decision:**  
The parallel trends assumption is violated. Standard pooled ITS is inappropriate. Must use segment-specific models allowing heterogeneous treatment effects.

---

## Methodology: Interrupted Time Series

ITS analysis estimates causal effects by comparing actual post-intervention outcomes to a projected counterfactual based on pre-intervention trends.

**Segmented regression specification:**

```
ridership_t = β₀ + β₁(time) + β₂(post_intervention) + β₃(time_since_intervention) + Σ(month_FE) + ε_t
```

**Parameters:**
- `β₁`: Pre-intervention trend (slope before intervention)
- `β₂`: Immediate level change at intervention
- `β₃`: Change in slope after intervention
- `month_FE`: Month fixed effects for seasonality

**Estimation approach:**
- Separate models for each route type (given non-parallel pre-trends)
- Newey-West HAC standard errors (accounting for autocorrelation)
- Counterfactual projection with 95% confidence intervals

---

## Learning Objectives

**Technical skills:**
- Segmented regression modeling for ITS
- Pre-trend validation and parallel trends testing
- Autocorrelation detection and correction
- Seasonality adjustment
- Counterfactual projection
- Sensitivity analysis and placebo tests

**Methodological judgment:**
- Recognizing when ITS assumptions are violated
- Choosing appropriate model specifications given violations
- Distinguishing causal effects from confounding
- Communicating results with honest uncertainty

**Portfolio development:**
- Clean, reproducible analysis workflow
- Professional documentation
- Transparent assumption testing
- Honest limitation acknowledgment

---

## Key References

**Methodological:**
- Bernal, J. L., Cummins, S., & Gasparrini, A. (2017). Interrupted time series regression for the evaluation of public health interventions: a tutorial. *International Journal of Epidemiology*, 46(1), 348-355.
- Cunningham, S. (2021). *Causal Inference: The Mixtape*. Yale University Press.

**Statistical Implementation:**
- statsmodels documentation for time series analysis
- Durbin-Watson test for autocorrelation
- Newey-West standard errors for HAC estimation

---

## Notes and Caveats

**On synthetic data:**  
This analysis uses synthetic data where true treatment effects are known. This enables validation that isn't possible with real-world data, making it ideal for learning and methodology development. In practice, true effects are unknown, making transparent assumption testing and honest uncertainty communication even more critical.

**On assumption violations:**  
The non-parallel pre-trends discovered in EDA represent a real methodological challenge, not a data quality issue. Working through this violation - and choosing defensible approaches despite imperfect assumptions - is valuable preparation for real-world analytics where perfect identification is rare.

---

## Portfolio Context

This project is part of my causal inference learning journey:

1. **RDD Analysis** - [Free Shipping Threshold Effects](https://github.com/tomasz-solis/rdd-free-shipping)
2. **Simple DiD** - [Marketing Campaign Impact](https://github.com/tomasz-solis/marketing-campaign-causal-impact)
3. **Staggered DiD** - [IPO Lockups](https://github.com/tomasz-solis/ipo-lockup-did-analysis)
4. **Interupted time series** - *This project* Ridership

---

## Contact

**Tomasz Solis**
- Email: tomasz.solis@gmail.com
- [LinkedIn](https://www.linkedin.com/in/tomaszsolis/)
- [GitHub](https://github.com/tomasz-solis)
