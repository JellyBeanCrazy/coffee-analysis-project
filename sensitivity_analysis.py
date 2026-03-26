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


    avg_scores = {country: np.mean(scores) for country, scores in all_scores.items()}
    
    sorted_avg = pd.DataFrame.from_dict(avg_scores, orient='index', columns=['avg_score'])
    
    sorted_avg = sorted_avg.sort_values(by='avg_score', ascending=False).head(10)

    return sorted_avg

def plot_results(df):
    plt.figure(figsize=(12, 6))
    
    # Identify the column to plot. 
    # If you didn't name it, it might be 0 or 'final_score'
    score_col = df.columns[0] 
    
    # Plot using the DataFrame method
    df[score_col].plot(kind='bar', color='skyblue', edgecolor='navy')
    
    plt.title("Stability Analysis: Average Country Scores", fontsize=14)
    plt.xlabel("Country of Origin", fontsize=12)
    plt.ylabel("Average Final Score", fontsize=12)
    plt.xticks(rotation=45)
    
    # Add data labels on top of bars for clarity
    for i, v in enumerate(df[score_col]):
        plt.text(i, v + 0.01, f"{v:.2f}", ha='center', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig("coffee_stability_plot.png")
    plt.show()
