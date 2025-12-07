"""
Generate REALISTIC transit ridership dataset for ITS analysis.

This dataset mimics real-world conditions:
- Small treatment effects (hard to detect)
- Higher noise (messy data)
- Confounding events (other things happening)
- Stronger seasonality

Designed to practice:
- Dealing with ambiguous results
- Communicating uncertainty
- Identifying confounders
- Making recommendations despite noise
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)

# ============================================================================
# DATASET PARAMETERS
# ============================================================================

# Date range (same as baseline)
START_DATE = datetime(2020, 1, 6)  # Monday
END_DATE = datetime(2024, 12, 30)  # Monday
INTERVENTION_DATE = datetime(2024, 1, 1)

# Generate weekly dates
dates = []
current_date = START_DATE
while current_date <= END_DATE:
    dates.append(current_date)
    current_date += timedelta(days=7)

n_weeks = len(dates)
print(f"Generating {n_weeks} weeks of data ({START_DATE.date()} to {END_DATE.date()})")

# ============================================================================
# ROUTE-SPECIFIC PARAMETERS (REALISTIC)
# ============================================================================

# Much smaller effects than baseline, higher noise
route_params = {
    'Downtown': {
        'baseline': 500,           # Starting ridership
        'pre_trend': 2.45,         # Same growth trend as baseline
        'treatment_effect': 50,    # SMALL effect (was 300 in baseline)
        'slope_change': 0,         # No trend change
        'noise_std': 60,           # 3x higher noise (was 20)
        'seasonality_amp': 80      # Stronger seasonality (was 30)
    },
    'Suburban': {
        'baseline': 400,
        'pre_trend': 1.67,
        'treatment_effect': 30,    # SMALL (was 200)
        'slope_change': 0,
        'noise_std': 45,           # 3x higher (was 15)
        'seasonality_amp': 60
    },
    'Cross-town': {
        'baseline': 300,
        'pre_trend': 1.09,
        'treatment_effect': 15,    # VERY SMALL (was 150)
        'slope_change': 0,
        'noise_std': 36,           # 3x higher (was 12)
        'seasonality_amp': 40
    }
}

# ============================================================================
# CONFOUNDING EVENTS
# ============================================================================

# These will affect ridership independently of express lanes
confounders = {
    'competitor_launch': {
        'date': datetime(2023, 7, 1),
        'effect': {
            'Downtown': -15,      # Competitor hurts Downtown most
            'Suburban': -8,       # Less impact on Suburban
            'Cross-town': -3      # Minimal on Cross-town
        },
        'ramp_weeks': 8           # Effect builds over 8 weeks
    },
    'gas_spike': {
        'date': datetime(2022, 3, 1),
        'duration_weeks': 16,     # Spike lasts 4 months
        'peak_effect': {
            'Downtown': +12,      # Gas spike helps transit
            'Suburban': +18,      # Especially suburban routes
            'Cross-town': +10
        }
    },
    'severe_winter': {
        'date': datetime(2023, 1, 1),
        'duration_weeks': 8,      # Two months of bad weather
        'effect': {
            'Downtown': -20,      # Bad weather hurts all routes
            'Suburban': -25,
            'Cross-town': -15
        }
    }
}

# ============================================================================
# GENERATE DATA
# ============================================================================

def apply_competitor_effect(date, route_type):
    """Competitor bus service launched Jul 2023 - gradual negative effect."""
    launch_date = confounders['competitor_launch']['date']
    if date < launch_date:
        return 0
    
    weeks_since = (date - launch_date).days / 7
    ramp_weeks = confounders['competitor_launch']['ramp_weeks']
    max_effect = confounders['competitor_launch']['effect'][route_type]
    
    # Ramp up over time, then stay constant
    if weeks_since <= ramp_weeks:
        return max_effect * (weeks_since / ramp_weeks)
    else:
        return max_effect

def apply_gas_spike_effect(date, route_type):
    """Gas price spike Mar-Jun 2022 - temporary positive effect."""
    spike_start = confounders['gas_spike']['date']
    duration = confounders['gas_spike']['duration_weeks']
    spike_end = spike_start + timedelta(weeks=duration)
    
    if date < spike_start or date > spike_end:
        return 0
    
    weeks_in = (date - spike_start).days / 7
    peak_effect = confounders['gas_spike']['peak_effect'][route_type]
    
    # Bell curve: rise to peak at midpoint, then fall
    progress = weeks_in / duration
    return peak_effect * np.sin(progress * np.pi)

def apply_severe_winter_effect(date, route_type):
    """Severe winter Jan-Feb 2023 - temporary negative effect."""
    winter_start = confounders['severe_winter']['date']
    duration = confounders['severe_winter']['duration_weeks']
    winter_end = winter_start + timedelta(weeks=duration)
    
    if date < winter_start or date > winter_end:
        return 0
    
    return confounders['severe_winter']['effect'][route_type]

def generate_realistic_data():
    """Generate complete realistic dataset with confounders."""
    
    all_data = []
    
    for route_type, params in route_params.items():
        print(f"\nGenerating {route_type} data...")
        
        for i, date in enumerate(dates):
            # Time variables
            weeks_from_start = i
            post_intervention = 1 if date >= INTERVENTION_DATE else 0
            weeks_since_intervention = max(0, (date - INTERVENTION_DATE).days / 7) if post_intervention else 0
            
            # Base trend
            base_ridership = params['baseline'] + (params['pre_trend'] * weeks_from_start)
            
            # Treatment effect (if post-intervention)
            treatment = params['treatment_effect'] * post_intervention
            slope_change = params['slope_change'] * weeks_since_intervention
            
            # Seasonality (stronger than baseline)
            month = date.month
            if month in [6, 7, 8]:  # Summer
                seasonality = -params['seasonality_amp']
            elif month in [12, 1, 2]:  # Winter
                seasonality = -params['seasonality_amp'] * 0.7
            else:
                seasonality = 0
            
            # CONFOUNDERS
            competitor = apply_competitor_effect(date, route_type)
            gas_effect = apply_gas_spike_effect(date, route_type)
            winter_effect = apply_severe_winter_effect(date, route_type)
            
            # Combine everything
            expected = (base_ridership + treatment + slope_change + 
                       seasonality + competitor + gas_effect + winter_effect)
            
            # Add noise (higher than baseline)
            noise = np.random.normal(0, params['noise_std'])
            actual = expected + noise
            
            # Ensure non-negative
            actual = max(0, actual)
            
            all_data.append({
                'date': date,
                'route_type': route_type,
                'avg_ridership': round(actual, 1),
                'post_intervention': post_intervention,
                'time_since_intervention': weeks_since_intervention
            })
    
    df = pd.DataFrame(all_data)
    return df

# ============================================================================
# GENERATE AND SAVE
# ============================================================================

print("="*60)
print("GENERATING REALISTIC DATASET")
print("="*60)

df_realistic = generate_realistic_data()

# Save
output_path = '../data/hard_mode/transit_ridership_realistic.csv'
df_realistic.to_csv(output_path, index=False)

print("\n" + "="*60)
print("REALISTIC DATASET GENERATED")
print("="*60)
print(f"Saved to: {output_path}")
print(f"Total observations: {len(df_realistic):,}")
print(f"Date range: {df_realistic['date'].min().date()} to {df_realistic['date'].max().date()}")
print(f"Route types: {df_realistic['route_type'].unique().tolist()}")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "="*60)
print("SUMMARY BY ROUTE AND PERIOD")
print("="*60)

for route in ['Downtown', 'Suburban', 'Cross-town']:
    route_data = df_realistic[df_realistic['route_type'] == route]
    
    pre = route_data[route_data['post_intervention'] == 0]['avg_ridership']
    post = route_data[route_data['post_intervention'] == 1]['avg_ridership']
    
    print(f"\n{route}:")
    print(f"  Pre-intervention mean:  {pre.mean():7.1f} riders (std: {pre.std():.1f})")
    print(f"  Post-intervention mean: {post.mean():7.1f} riders (std: {post.std():.1f})")
    print(f"  Naive difference:       {post.mean() - pre.mean():+7.1f} riders")

# ============================================================================
# RAW JUMP AT INTERVENTION (for validation)
# ============================================================================

print("\n" + "="*60)
print("RAW JUMP AT INTERVENTION (for reference)")
print("="*60)
print("\nNote: These include confounders + noise, so won't exactly match")
print("true treatment effects. That's the point - this is realistic!")

for route in ['Downtown', 'Suburban', 'Cross-town']:
    route_data = df_realistic[df_realistic['route_type'] == route].sort_values('date')
    
    last_pre = route_data[route_data['date'] < INTERVENTION_DATE].iloc[-1]
    first_post = route_data[route_data['date'] >= INTERVENTION_DATE].iloc[0]
    
    raw_jump = first_post['avg_ridership'] - last_pre['avg_ridership']
    true_effect = route_params[route]['treatment_effect']
    
    print(f"\n{route}:")
    print(f"  Last pre:  {last_pre['avg_ridership']:6.1f} riders ({last_pre['date'].date()})")
    print(f"  First post: {first_post['avg_ridership']:6.1f} riders ({first_post['date'].date()})")
    print(f"  Raw jump:  {raw_jump:+6.1f} riders")
    print(f"  True treatment effect: {true_effect:+6.1f} riders")
    print(f"  Note: Raw jump includes confounders + noise")

# ============================================================================
# CONFOUNDER SUMMARY
# ============================================================================

print("\n" + "="*60)
print("CONFOUNDING EVENTS IN DATA")
print("="*60)

print("\n1. Competitor Bus Service (Jul 2023)")
print("   - Gradual negative effect on ridership")
print("   - Stronger impact on Downtown routes")
print("   - Challenge: Happens 6 months BEFORE express lanes")

print("\n2. Gas Price Spike (Mar-Jun 2022)")
print("   - Temporary boost to transit ridership")
print("   - Bell curve effect over 4 months")
print("   - Challenge: Well before intervention, but affects pre-trend")

print("\n3. Severe Winter (Jan-Feb 2023)")
print("   - 2-month dip in ridership")
print("   - All routes affected")
print("   - Challenge: Creates noise in pre-period")

print("\n" + "="*60)
print("✓ Dataset ready for realistic ITS analysis")
print("="*60)

print("\nGround truth treatment effects:")
for route, params in route_params.items():
    print(f"  {route:12s}: {params['treatment_effect']:+3d} riders (immediate level change)")

print("\nExpected challenges:")
print("  - Small effects + high noise = wider confidence intervals")
print("  - Competitor confounder may bias results downward")
print("  - Gas spike affects pre-trend estimation")
print("  - Some effects may not reach statistical significance")
print("\nThis is what real analytics looks like!")
print("="*60)