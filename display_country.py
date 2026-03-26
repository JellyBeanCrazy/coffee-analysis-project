import numpy as np
import pandas as pd

def analysis(df, manual_adjustments=False, custom_weights_dict=None):
    """
    Analyzes coffee data by country, applying weights to normalized metrics.
    If manual_adjustments is True, prompts the user for custom weights.
    """
    
    # 1. Define Metric Categories
    primary_quality = ['flavor', 'aroma', 'body', 'uniformity', 'cupper_points']
    secondary_quality = ['aftertaste', 'acidity', 'balance', 'clean_cup', 'sweetness', 'moisture']
    strategic_metrics = ['process_score', 'caffeine_score', 'producer_count']

    # 2. Set Default Weights
    # We use a dictionary to keep track of how much each column "matters"
    weights = {metric: 1.0 for metric in primary_quality}
    weights.update({metric: 0.3 for metric in secondary_quality})
    weights.update({metric: 1.0 for metric in strategic_metrics})

    # 3. Handle User Adjustments
    if custom_weights_dict:
        weights = custom_weights_dict
    elif manual_adjustments:
        print("\n--- Custom Weighting Configuration ---")
        print("Press 'Enter' to keep the default weight, or type a number (e.g., 1.5 or 0.5)")
        for metric in weights.keys():
            user_input = input(f"Weight for {metric} (Default {weights[metric]}): ").strip()
            if user_input:
                try:
                    weights[metric] = float(user_input)
                except ValueError:
                    print(f"Invalid input for {metric}. Keeping default: {weights[metric]}")

    # 4. Data Pre-Processing (Calculated on the raw DataFrame)
    # Mapping Washed/Semi-washed to 1.0, others to 0.2
    preferred_methods = ['Washed / Wet', 'Semi-washed / Semi-pulped']
    df['process_score'] = np.where(df['processing_method'].isin(preferred_methods), 1.0, 0.2)
    
    # Mapping Arabica to 1.0 (Low Caffeine), Robusta to 0.0
    df['caffeine_score'] = np.where(df['species'] == 'Arabica', 1.0, 0.0)

    # 5. Aggregate Data by Country
    all_metrics = primary_quality + secondary_quality + ['process_score', 'caffeine_score']
    
    country_stats = df.groupby('country_of_origin').agg({
        **{feat: 'mean' for feat in all_metrics},
        'country_of_origin': 'count'
    }).rename(columns={'country_of_origin': 'producer_count'})

    # 6. Normalization (Scale everything 0.0 to 1.0)
    # This prevents 'producer_count' from overpowering 'flavor'
    stats_norm = (country_stats - country_stats.min()) / (country_stats.max() - country_stats.min())

    # 7. Final Score Calculation
    # We calculate the score by multiplying the normalized value by the weight
    country_stats['final_score'] = 0
    for metric, weight in weights.items():
        country_stats['final_score'] += stats_norm[metric] * weight

    # 8. Save to HTML Report
    # Sort by final score before saving
    full_report = country_stats.sort_values('final_score', ascending=False).round(2)
    
    style = """
    <style>
        table { border-collapse: collapse; width: 100%; font-family: sans-serif; }
        th, td { text-align: left; padding: 12px; border: 1px solid #ddd; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        tr:hover { background-color: #ddd; }
    </style>
    """
    
    with open("coffee_analysis_full_report.html", "w") as f:
        f.write("<html><head><title>Coffee Country Ranking</title></head><body>")
        f.write(style)
        f.write("<h1>Comprehensive Country Leaderboard</h1>")
        f.write(full_report.to_html())
        f.write("</body></html>")

    # 9. Return Top 5 for the terminal/main script
    return full_report.head(5)