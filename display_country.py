import numpy as np
import pandas as pd

def analysis(df, top_N):
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
    # 1. Define Priority Tiers
    primary_quality = ['flavor', 'aroma', 'body', 'uniformity', 'cupper_points']
    secondary_quality = [
        'aftertaste', 'acidity', 'balance', 'clean_cup', 
        'sweetness', 'moisture'
    ]
    
    # 2. Process Strategic Categories
    preferred_methods = ['Washed / Wet', 'Semi-washed / Semi-pulped']
    df['process_score'] = np.where(df['processing_method'].isin(preferred_methods), 1.0, 0.2)
    
    df['caffeine_score'] = np.where(df['species'] == 'Arabica', 1.0, 0.0)

    # 3. Aggregate Data
    all_metrics = primary_quality + secondary_quality + ['process_score', 'caffeine_score']
    
    country_stats = df.groupby('country_of_origin').agg({
        **{feat: 'mean' for feat in all_metrics},
        'country_of_origin': 'count'
    }).rename(columns={'country_of_origin': 'producer_count'})

    # 4. Normalization (0.0 to 1.0 scale)
    stats_norm = (country_stats - country_stats.min()) / (country_stats.max() - country_stats.min())

    # 5. Weighted Final Score Calculation
    primary_sum = stats_norm[primary_quality].sum(axis=1)
    
    secondary_sum = stats_norm[secondary_quality].sum(axis=1) * 0.3
    
    strategy_sum = (
        stats_norm['process_score'] + 
        stats_norm['caffeine_score'] + 
        stats_norm['producer_count']
    )

    country_stats['final_score'] = primary_sum + secondary_sum + strategy_sum
    html_output = country_stats.round(2).sort_values('final_score', ascending=False).to_html()
    
    with open("coffee_analysis_full_report.html", "w") as f:
        f.write("<html><head><title>Coffee Country Analysis</title></head><body>")
        f.write("<h1>Full Country Ranking</h1>")
        f.write(html_output)
        f.write("</body></html>")
    
    # 6. Return Top_N sorted by Final Score
    return country_stats.sort_values('final_score', ascending=False).head(top_N)
