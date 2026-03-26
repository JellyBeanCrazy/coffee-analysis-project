import numpy as np
import pandas as pd

def analysis(df, manual_adjustments=False, custom_weights_dict=None):
    """
    Analyses the coffee ratings data to find the top recommended countries to 
    source coffee from. Each country is given a final score based on a weighted 
    combination of quality measures, processing method, caffeine content, and 
    number of producers. The results are saved as a HTML report and the top N 
    countries are returned.

    The scoring works as follows:
        - Primary quality measures (flavour, aroma, body, uniformity, cupper points) 
          are weighted highest as these are what the client's customers care most about.
        - Secondary quality measures (aftertaste, acidity, balance etc.) are included 
          at a lower weight of 0.3 as they are still relevant but less important.
        - Processing method is scored 1.0 for washed/wet methods and 0.2 for others, 
          as the client prefers washed processing for a more consistent flavour.
        - Caffeine content is scored 1.0 for Arabica (lower caffeine) and 0.0 for 
          Robusta, as the client's customers prefer lower caffeine coffee.
        - Producer count rewards countries with more producers, giving buyers more 
          choice during their visit.

    Parameters:
        df (pd.DataFrame): The cleaned coffee ratings dataset.
        top_N (int): The number of top countries to return, for example 5 would 
        return the 5 highest scoring countries.

    Returns:
        pd.DataFrame: A table of the top N countries sorted by their final score, 
        highest first.
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
