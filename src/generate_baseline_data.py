"""
Generate Baseline Transit Ridership Dataset for ITS Analysis

This creates "easy mode" synthetic data with:
- Large, obvious treatment effects (300, 200, 150 riders)
- Minimal noise and seasonality
- Clear visual jumps at intervention
- Known ground truth for validation

Purpose: Learn ITS mechanics before tackling messier realistic data.

Author: Tomasz Solis
Date: December 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)

# Time parameters
start_date = datetime(2020, 1, 6)  # Monday
end_date = datetime(2024, 12, 30)
intervention_date = datetime(2024, 1, 1)

# Generate weekly dates
dates = []
current_date = start_date
while current_date <= end_date:
    dates.append(current_date)
    current_date += timedelta(days=7)

# Route types with different parameters
routes = ['Downtown', 'Suburban', 'Cross-town']

# Parameters for each route (BASELINE VERSION - LARGE EFFECTS)
route_params = {
    'Downtown': {
        'base_ridership': 500,
        'pre_trend': 2.45,  # riders per week growth
        'treatment_effect': 300,  # LARGE immediate jump
        'slope_change': 0,  # no change in growth rate
        'noise_std': 20  # low noise for clarity
    },
    'Suburban': {
        'base_ridership': 400,
        'pre_trend': 1.67,
        'treatment_effect': 200,  # LARGE immediate jump
        'slope_change': 0,
        'noise_std': 15
    },
    'Cross-town': {
        'base_ridership': 300,
        'pre_trend': 1.09,
        'treatment_effect': 150,  # LARGE immediate jump
        'slope_change': 0,
        'noise_std': 12
    }
}

# Generate data
data = []

for route in routes:
    params = route_params[route]
    
    for i, date in enumerate(dates):
        # Time variables
        time = i
        post_intervention = 1 if date >= intervention_date else 0
        time_since_intervention = max(0, (date - intervention_date).days / 7)
        
        # Base ridership with linear trend
        ridership = params['base_ridership'] + (params['pre_trend'] * time)
        
        # Add MINIMAL seasonality (just a hint)
        month = date.month
        if month in [6, 7, 8]:  # Summer dip
            ridership -= 30
        if month in [12, 1]:  # Winter dip
            ridership -= 20
        
        # Treatment effect (immediate level change)
        if post_intervention:
            ridership += params['treatment_effect']
            ridership += params['slope_change'] * time_since_intervention
        
        # Add small random noise
        ridership += np.random.normal(0, params['noise_std'])
        
        # Record observation
        data.append({
            'date': date,
            'route_type': route,
            'avg_ridership': round(ridership, 1),
            'post_intervention': post_intervention,
            'time': time,
            'time_since_intervention': int(time_since_intervention)
        })

# Create DataFrame
df = pd.DataFrame(data)

# Sort by route and date
df = df.sort_values(['route_type', 'date']).reset_index(drop=True)

# Save to CSV
output_path = '../data/easy_mode/transit_ridership_baseline.csv'
df.to_csv(output_path, index=False)

print(f"\nSaved to: {output_path}")
print(f"Total observations: {len(df):,}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"\nRoute types: {df['route_type'].unique().tolist()}")

# Show summary by route and period

for route in routes:
    route_data = df[df['route_type'] == route]
    pre_data = route_data[route_data['post_intervention'] == 0]
    post_data = route_data[route_data['post_intervention'] == 1]
    
    pre_mean = pre_data['avg_ridership'].mean()
    post_mean = post_data['avg_ridership'].mean()
    diff = post_mean - pre_mean
    
    print(f"\n{route}:")
    print(f"  Pre-intervention mean:  {pre_mean:7.1f} riders")
    print(f"  Post-intervention mean: {post_mean:7.1f} riders")
    print(f"  Naive difference:       {diff:+7.1f} riders")

# Show the actual jump at intervention

for route in routes:
    route_data = df[df['route_type'] == route].sort_values('time')
    
    last_pre = route_data[route_data['post_intervention']==0].iloc[-1]
    first_post = route_data[route_data['post_intervention']==1].iloc[0]
    
    raw_jump = first_post['avg_ridership'] - last_pre['avg_ridership']
    expected_trend = route_params[route]['pre_trend']
    treatment = raw_jump - expected_trend
    
    print(f"\n{route}:")
    print(f"  Last pre:  {last_pre['avg_ridership']:7.1f} riders ({last_pre['date'].date()})")
    print(f"  First post: {first_post['avg_ridership']:7.1f} riders ({first_post['date'].date()})")
    print(f"  Raw jump: {raw_jump:+7.1f} riders")
    print(f"  Expected from trend: {expected_trend:+7.1f} riders")
    print(f"  Treatment effect: {treatment:+7.1f} riders ← Should match β₂ in ITS")

print("\nGround truth treatment effects:")
print("  Downtown:   +300 riders (immediate level change)")
print("  Suburban:   +200 riders (immediate level change)")
print("  Cross-town: +150 riders (immediate level change)")
print("  All slopes:    0 riders/week (no growth rate change)")
