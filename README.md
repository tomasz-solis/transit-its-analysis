# Interrupted Time Series Analysis: Transit Ridership Impact Study

**Author:** Tomasz Solis  
**Date:** December 2025  
**Objective:** Learning ITS methodology through baseline validation and realistic application

---

## Project Overview

This project applies Interrupted Time Series (ITS) analysis to measure the causal impact of express bus lanes on transit ridership. The analysis uses two synthetic datasets: a clean baseline for methodology validation, and a realistic dataset with confounders for practicing real-world analytics.

**Why this project exists:**  
ITS is a quasi-experimental method for policy evaluation when randomized experiments aren't feasible. This project is methodological practice - first validating ITS mechanics on clean data, then applying the same approach to messy data to learn how to communicate uncertain results honestly.


## The Research Question

**Did dedicated express bus lanes increase transit ridership?**

Metropolitan Transit Authority launched express bus lanes across the city on January 1, 2024. All routes were affected simultaneously (no control group), making this a natural candidate for ITS analysis.

**Key challenges:**
- Multiple route types with different baseline dynamics
- Non-parallel pre-intervention trends across segments
- Confounding events near intervention (realistic dataset)
- Small effects relative to noise (realistic dataset)

These mirror real-world complications in policy evaluation and product analytics.


## Datasets

### **Baseline Dataset (easy_mode)**
- 783 observations (261 weeks × 3 route types)
- January 2020 - December 2024
- Known treatment effects: +300, +200, +150 riders
- Low noise, large clear effects
- **Purpose:** Validate methodology works correctly

### **Realistic Dataset (hard_mode)**
- Same structure as baseline
- Known treatment effects: +50, +30, +15 riders (6-10x smaller)
- High noise (3x baseline variance)
- Confounders: Competitor launch (Jul 2023), gas spike (2022), severe winter (2023)
- **Purpose:** Practice handling messy real-world data


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
│       └── transit_ridership_realistic.csv
├── notebooks/
│   ├── 01_eda_baseline.ipynb           # Complete
│   ├── 02_its_model_baseline.ipynb     # Complete
│   ├── 03_robustness_checks.ipynb      # Complete
│   ├── 04_eda_realistic.ipynb          # Complete
│   ├── 05_its_model_realistic.ipynb    # Complete
│   └── 06_robustness_checks_realistic.ipynb  # Complete
├── outputs/
│   └── figures/                         # Generated plots
└── src/
    ├── generate_baseline_data.py
    └── generate_realistic_data.py
```


## Analysis Summary

### **Part 1: Baseline Dataset (Validation)**

**Notebooks 01-03:** EDA, ITS Model, Robustness Checks

**Results:**

| Route | True Effect | Estimated β₂ | Error | 95% CI | Significance |
|-------|-------------|--------------|-------|--------|--------------|
| Downtown | +300 | +307.7 | +2.6% | [294, 322] | p < 0.001 ✓ |
| Suburban | +200 | +202.5 | +1.3% | [182, 223] | p < 0.001 ✓ |
| Cross-town | +150 | +150.7 | +0.4% | [136, 165] | p < 0.001 ✓ |

**Robustness checks:**
- ✓ Placebo tests: 16% of real effects, 0/12 significant
- ✓ Window sensitivity: <5% variation
- ✓ Leave-one-out: 0% deviation (segment-specific models appropriate)
- ✓ Alternative specs: <6% deviation

**Conclusion:** ITS methodology validated. Estimates within ±3% of known effects, all assumptions satisfied, results extremely robust.


### **Part 2: Realistic Dataset (Practice)**

**Notebooks 04-06:** EDA, ITS Model, Robustness Checks

**EDA findings:**
- High pre-period noise: σ = 77-165 riders (vs 42-80 post-period)
- Naive differences: +366, +236, +157 (massively inflated by trends + confounders)
- Same non-parallel pre-trends (128% difference)
- **Critical confounder:** Competitor bus service launched Jul 2023, 6 months before intervention

**ITS results:**

| Route | True Effect | Estimated β₂ | Error | 95% CI | Significance |
|-------|-------------|--------------|-------|--------|--------------|
| Downtown | +50 | +53.0 | +6% | [9, 97] | p = 0.018 ✓ |
| Suburban | +30 | +23.4 | -22% | [-20, 67] | p = 0.292 ✗ |
| Cross-town | +15 | +7.2 | -52% | [-15, 29] | p = 0.519 ✗ |

**Key differences from baseline:**
- Only 1/3 routes statistically significant (vs 3/3)
- Errors: 6-52% (vs <3%)
- CI widths: ±22-44 riders (vs ±10-15)
- R²: 0.83-0.89 (vs 0.98-0.99)

**Robustness checks:**
- ⚠️ Placebo tests: 3/12 significant (25%), largest placebo 68.8 vs smallest real effect 7.2 (955% ratio)
- ⚠️ Window sensitivity: 28-83% variation (Downtown most stable, Cross-town very sensitive)
- ✓ Leave-one-out: Still 0% deviation
- ⚠️ Alternative specs: 62-98% deviation (very sensitive to modeling choices)

**Honest assessment:**

The realistic dataset results show **fragile evidence**, not just uncertainty:

**What worked:**
- Downtown route shows positive effect directionally
- All true effects fall within confidence intervals (not biased, just imprecise)
- Segment-specific approach still appropriate

**What didn't work:**
- Robustness checks reveal serious issues:
  - Placebo effects larger than real effects (red flag for noise)
  - Results very sensitive to time window and specification choices
  - Can't reliably distinguish signal from noise for Suburban/Cross-town
- Competitor confounder creates fundamental identification problem
- High noise overwhelms small effects

**What this teaches:**

This is what happens when ITS assumptions are badly violated:
- Concurrent confounders (competitor) bias the counterfactual
- Small effects + high noise = low statistical power
- Can get point estimates but can't trust them
- Modeling choices matter enormously

**In practice, I would report:**
"Results are inconclusive. Downtown shows directional evidence of positive effects, but competitor confounder and high noise prevent reliable quantification. Suburban and Cross-town effects not detectable. Would need either:<br>
(1) more post-intervention data to improve precision,<br>
(2) complementary analysis method,<br>
(3) acknowledge we can't measure this cleanly."<br>

This is the honest reality of messy observational data - sometimes you can't get clean answers, and acknowledging that is better than overselling weak results.


## Methodology: Interrupted Time Series

ITS estimates causal effects by comparing actual post-intervention outcomes to a projected counterfactual based on pre-intervention trends.

**Segmented regression specification:**

```
ridership_t = β₀ + β₁(time) + β₂(post_intervention) + β₃(time_since_intervention) + ε_t
```

**Parameters:**
- `β₁`: Pre-intervention trend (slope before intervention)
- `β₂`: Immediate level change at intervention ← **Key causal effect**
- `β₃`: Change in slope after intervention

**Estimation approach:**
- Separate models for each route type (non-parallel pre-trends)
- Newey-West HAC standard errors (autocorrelation)
- Counterfactual projection with 95% confidence intervals

**Critical assumptions:**
1. Stable pre-intervention trend would have continued
2. No concurrent confounding events at intervention time
3. No anticipation effects
4. Correct functional form for trend


## Learning Objectives Achieved

**Technical skills:**
✓ Segmented regression for ITS  
✓ Pre-trend validation and non-parallel trends handling  
✓ Autocorrelation detection and correction (Newey-West)  
✓ Counterfactual projection with uncertainty  
✓ Comprehensive robustness testing  
✓ Placebo tests and falsification  

**Methodological judgment:**
✓ Recognizing when assumptions are violated  
✓ Distinguishing validation (baseline) from application (realistic)  
✓ Understanding when results are too fragile to trust  
✓ Communicating uncertainty and limitations honestly  
✓ Knowing when to say "the data can't answer this question cleanly"

**Key insight:**
Perfect causal inference is rare. The baseline dataset shows ITS CAN work beautifully when assumptions hold. The realistic dataset shows what happens when they don't - and that being honest about weak evidence is more valuable than overselling it.


## Key Takeaways

**From baseline analysis:**
- ITS methodology validated - works correctly on clean data
- Segment-specific models handle non-parallel pre-trends
- Robustness checks confirm when results are trustworthy

**From realistic analysis:**
- Small effects + high noise + confounders = fragile results
- Placebo tests catching noise as "effects" is a major red flag
- Concurrent events (competitor) create fundamental identification problems
- Sometimes the honest answer is "we can't measure this reliably"

**For future work:**
- When facing similar scenarios, consider:
  - Waiting for more post-intervention data
  - Finding a control group (switch to DiD if possible)
  - Using complementary methods (surveys, experiments)
  - Being transparent about what's unknowable


## References

**Methodological:**
- Bernal, J. L., Cummins, S., & Gasparrini, A. (2017). Interrupted time series regression for the evaluation of public health interventions: a tutorial. *International Journal of Epidemiology*, 46(1), 348-355.
- Cunningham, S. (2021). *Causal Inference: The Mixtape*. Yale University Press.

**Statistical Implementation:**
- statsmodels documentation for time series analysis
- Durbin-Watson test for autocorrelation
- Newey-West standard errors for HAC estimation


## Notes

**On synthetic data:**  
Both datasets use synthetic data with known true effects. This enables validation impossible with real-world data. In practice, true effects are unknown, making transparent assumption testing and honest uncertainty communication even more critical.

**On the realistic dataset:**  
The weak robustness isn't a failure - it's exactly what this dataset was designed to teach. Real product analytics often faces these conditions: small effects, high noise, confounding events. Learning to recognize when evidence is too weak to trust is as important as learning when it's strong.


## Portfolio Context

This project is part of my causal inference learning journey:

1. **RDD Analysis** - [Free Shipping Threshold Effects](https://github.com/tomasz-solis/rdd-free-shipping)
2. **Simple DiD** - [Marketing Campaign Impact](https://github.com/tomasz-solis/marketing-campaign-causal-impact)
3. **Staggered DiD** - [IPO Lockups](https://github.com/tomasz-solis/ipo-lockup-did-analysis)
4. **Interrupted Time Series** - *This project*


## Contact

**Tomasz Solis**
- Email: tomasz.solis@gmail.com
- [LinkedIn](https://www.linkedin.com/in/tomaszsolis/)
- [GitHub](https://github.com/tomasz-solis)
