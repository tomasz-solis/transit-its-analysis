# Interrupted Time Series Analysis: Transit Ridership Impact Study

**Author:** Tomasz Solis  
**Date:** December 2025  
**Objective:** ITS methodology practice using synthetic transit data

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
- Known treatment effects: +300, +200, +150 riders for validation

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
│   ├── 01_eda_baseline.ipynb           # Complete: EDA and assumption testing
│   ├── 02_its_model_baseline.ipynb     # Complete: ITS analysis with validation
│   └── 03_robustness_checks.ipynb      # Complete: Placebo, sensitivity, spec tests
├── outputs/
│   ├── figures/                         # Generated plots (10 total)
│   └── results/                         # Model outputs and tables
└── src/
    └── generate_baseline_data.py        # Data generation script
```

---

## Current Progress

### Completed: Exploratory Data Analysis

**Notebook:** `01_eda_baseline.ipynb`

**Key findings:**

1. **Data Quality:** Complete dataset, no missing values, consistent 7-day intervals

2. **Pre-Intervention Trends:** NOT parallel across route types
   - Downtown: 2.47 riders/week growth
   - Suburban: 1.66 riders/week growth
   - Cross-town: 1.09 riders/week growth
   - Downtown growing 2.27x faster than Cross-town (127% difference)

3. **Seasonality:** Minimal in baseline dataset (by design for learning)
   - Summer/winter dips present but small
   - No month fixed effects needed for baseline analysis

4. **Visual Evidence:** Large, obvious level increases at January 2024 across all routes

5. **Autocorrelation:** Detected (Durbin-Watson < 2.0)
   - Addressed with Newey-West robust standard errors

**Critical methodological decision:**  
The parallel trends assumption is violated. Standard pooled ITS is inappropriate. Using segment-specific models allowing heterogeneous treatment effects.

---

### Completed: ITS Segmented Regression Analysis

**Notebook:** `02_its_model_baseline.ipynb`

**Model specification:**
```
ridership_t = β₀ + β₁(time) + β₂(post_intervention) + β₃(time_since_intervention) + ε_t
```

**Results:**

| Route Type | True Effect | Estimated β₂ | Error | 95% CI | R² |
|------------|-------------|--------------|-------|--------|-----|
| Downtown | +300 riders | +307.7 | +2.6% | [293.8, 321.6] | 0.993 |
| Suburban | +200 riders | +202.5 | +1.3% | [182.3, 222.7] | 0.989 |
| Cross-town | +150 riders | +150.7 | +0.4% | [136.3, 165.0] | 0.983 |

**Validation: PASSED**
- All estimates within ±3% of true treatment effects
- All true effects fall within 95% confidence intervals
- Model fit excellent (R² > 0.98) across all route types
- Treatment effects stable throughout post-intervention period

**Key technical choices:**
- Separate OLS models for each route type (non-parallel pre-trends)
- Newey-West HAC standard errors (maxlags=4) for autocorrelation
- No month fixed effects (minimal seasonality + confounding with Jan 1 intervention)
- Counterfactual validation against known ground truth

**What I learned:**
- Month fixed effects trap: When intervention timing coincides with calendar periods (January 1), standard seasonal dummies create multicollinearity and absorb treatment effects
- Segment-specific modeling handles non-parallel pre-trends effectively
- Validation against synthetic data confirms methodology before applying to real data
- Treatment effect stability over time supports causal interpretation

---

### Completed: Robustness Checks

**Notebook:** `03_robustness_checks.ipynb`

**What I tested:**

1. **Placebo Tests** (12 fake intervention dates)
   - Tested Jan 2022, Jul 2022, Jan 2023, Jul 2023
   - Result: Placebo estimates ~16% of real effects
   - Conclusion: Model not finding spurious patterns

2. **Window Sensitivity** (1-4 years of pre-data)
   - Tested 1, 2, 3, 4 year pre-intervention periods
   - Result: <5% variation across windows
   - Conclusion: Not sensitive to historical period choice

3. **Leave-One-Out Validation** (exclude each route)
   - Tested excluding Downtown, Suburban, Cross-town
   - Result: 0% deviation (expected with segment-specific models)
   - Conclusion: Confirms segmentation approach was appropriate

4. **Alternative Specifications** (~15 spec variants)
   - Newey-West lags: 2, 4, 6, 8 weeks
   - Boundary exclusions: first month, last month, both
   - Slope change: allowed β₃ ≠ 0
   - Result: <6% worst-case deviation
   - Conclusion: Not sensitive to modeling choices

**Overall assessment:**
- Placebo tests: PASSED (16% of real effects)
- Window tests: EXCELLENT (<5% variation)
- Leave-one-out: EXCELLENT (0% deviation)
- Specification tests: EXCELLENT (<6% deviation)

**Interpretation:**  
The +300/+200/+150 rider effects appear robust to falsification tests, time window choices, and specification alternatives. Results suggest the ITS methodology is working correctly on this baseline dataset.

**Caveats:**  
This is synthetic data with known ground truth and large, clear effects by design. Real-world analysis would show more sensitivity and require more judgment about which specifications are appropriate.

---

## Methodology: Interrupted Time Series

ITS analysis estimates causal effects by comparing actual post-intervention outcomes to a projected counterfactual based on pre-intervention trends.

**Segmented regression specification:**

```
ridership_t = β₀ + β₁(time) + β₂(post_intervention) + β₃(time_since_intervention) + ε_t
```

**Parameters:**
- `β₁`: Pre-intervention trend (slope before intervention)
- `β₂`: Immediate level change at intervention ← **Key causal effect**
- `β₃`: Change in slope after intervention

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
- Counterfactual projection
- Placebo tests and falsification
- Sensitivity analysis and specification robustness

**Methodological judgment:**
- Recognizing when ITS assumptions are violated
- Choosing appropriate model specifications given violations
- Distinguishing causal effects from confounding
- Systematically interrogating findings
- Communicating results with honest uncertainty

---

## Next Steps

**Apply to realistic dataset**
- Smaller, ambiguous treatment effects (~50, ~30, ~15 riders)
- More noise and confounders
- Practice communicating uncertain results
- "This is what real analytics looks like"

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
4. **Interrupted Time Series** - *This project*

---

## Contact

**Tomasz Solis**
- Email: tomasz.solis@gmail.com
- [LinkedIn](https://www.linkedin.com/in/tomaszsolis/)
- [GitHub](https://github.com/tomasz-solis)
