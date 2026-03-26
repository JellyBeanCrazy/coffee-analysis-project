from display_country import analysis
import pandas as pd

import matplotlib.pyplot as plt
import random
import numpy as np

def run_parameter_sweep(df, iterations=50):
    metrics = ['flavor', 'aroma', 'body', 'uniformity', 'cupper_points', 
               'aftertaste', 'acidity', 'balance', 'clean_cup', 'sweetness', 
               'moisture', 'process_score', 'caffeine_score', 'producer_count']
    
    ranges = {}
    print(f"\n--- Define Weight Ranges (e.g., Min 0.5, Max 1.5) ---")
    for m in metrics:
        print(f"\nSettings for: {m}")
        low = float(input(f"  Min weight for {m}: ") or 0.5)
        high = float(input(f"  Max weight for {m}: ") or 1.5)
        ranges[m] = (low, high)

    # Dictionary to store accumulated scores
    all_scores = {}

    print(f"Running {iterations} simulations...")
    for _ in range(iterations):
        # Generate a random weight set based on the user's ranges
        current_weights = {m: random.uniform(r[0], r[1]) for m, r in ranges.items()}
        
        # We need to modify our analysis function slightly to accept a pre-built dict
        # For now, let's assume we pass this dict directly
        results = analysis(df, custom_weights_dict=current_weights)
        
        for country, row in results.iterrows():
            all_scores[country] = all_scores.get(country, []) + [row['final_score']]

    # Calculate Average Scores
    avg_scores = {country: np.mean(scores) for country, scores in all_scores.items()}
    sorted_avg = pd.Series(avg_scores).sort_values(ascending=False).head(10)

    plot_results(sorted_avg)
    return sorted_avg

def plot_results(series):
    plt.figure(figsize=(10, 6))
    series.plot(kind='bar', color='skyblue', edgecolor='navy')
    plt.title("Stability Analysis: Average Country Scores across Parameter Sweep")
    plt.xlabel("Country of Origin")
    plt.ylabel("Average Final Score")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("coffee_stability_plot.png")
    print("\nGraph saved as 'coffee_stability_plot.png'")
    plt.show()

