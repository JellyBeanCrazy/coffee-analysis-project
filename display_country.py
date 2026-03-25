import numpy as np
import pandas as pd


def analysis(df):
    # 1. Define Priority Tiers
    # Primary: Core buyer requirements + Cupper Points (Weight 1.0)    primary_quality = ['flavor', 'aroma', 'body', 'uniformity', 'cupper_points']
    primary_quality = ['flavor', 'aroma', 'body', 'uniformity', 'cupper_points']
    # Secondary: Supporting sensory metrics (Weight 0.3)
    secondary_quality = [
        'aftertaste', 'acidity', 'balance', 'clean_cup', 
        'sweetness', 'moisture'
    ]
    
    # 2. Process Strategic Categories
    # Mapping Washed/Semi-washed to 1.0, others to 0.2
    preferred_methods = ['Washed / Wet', 'Semi-washed / Semi-pulped']
    df['process_score'] = np.where(df['processing_method'].isin(preferred_methods), 1.0, 0.2)
    
    # Mapping Arabica to 1.0 (Low Caffeine), Robusta to 0.0
    df['caffeine_score'] = np.where(df['species'] == 'Arabica', 1.0, 0.0)

    # 3. Aggregate Data
    all_metrics = primary_quality + secondary_quality + ['process_score', 'caffeine_score']
    
    country_stats = df.groupby('country_of_origin').agg({
        **{feat: 'mean' for feat in all_metrics},
        'country_of_origin': 'count'
    }).rename(columns={'country_of_origin': 'producer_count'})

    # 4. Normalization (0.0 to 1.0 scale)
    # This ensures a '9' in Flavor is compared fairly against a '500' in Producer Count
    stats_norm = (country_stats - country_stats.min()) / (country_stats.max() - country_stats.min())

    # 5. Weighted Final Score Calculation
    # High Priority (1.0x)
    primary_sum = stats_norm[primary_quality].sum(axis=1)
    
    # Lower Priority (0.3x)
    secondary_sum = stats_norm[secondary_quality].sum(axis=1) * 0.3
    
    # Strategic Weights (1.0x)
    strategy_sum = (
        stats_norm['process_score'] + 
        stats_norm['caffeine_score'] + 
        stats_norm['producer_count']
    )

    country_stats['final_score'] = primary_sum + secondary_sum + strategy_sum

    # --- NEW: SAVE TO FILE ---
    # Round to 2 decimals so the table looks clean
    html_output = country_stats.round(2).sort_values('final_score', ascending=False).to_html()
    
    with open("coffee_analysis_full_report.html", "w") as f:
        f.write("<html><head><title>Coffee Country Analysis</title></head><body>")
        f.write("<h1>Full Country Ranking</h1>")
        f.write(html_output)
        f.write("</body></html>")
    # 6. Return Top 5 sorted by Final Score
    return country_stats.sort_values('final_score', ascending=False).head(5)