from display_country import analysis
import pandas as pd
df = pd.read_csv(r"data/simplified_coffee_ratings.csv")
df.columns = df.columns.str.strip().str.lower() # Cleans spaces and matches case
results = analysis(df)
# Display the top 5 countries and their calculated scores
print("--- Top 5 Recommended Countries ---")
print(results[['final_score', 'producer_count', 'flavor', 'aroma', 'body', 'uniformity', 'cupper_points', 'aftertaste',
       'acidity', 'balance', 'clean_cup', 'sweetness', 'moisture', 'process_score', 'caffeine_score']])
# Save the Top 5 specifically
results.to_csv("top_5_countries.csv")
print("\nResults successfully saved to 'top_5_countries.csv'")
# Optional: Access just the #1 recommendation
best_country = results.index[0]
print(f"\nThe best country to send the buyer to is: {best_country}")

# print(results.columns)
# df = pd.read_csv(r"data/simplified_coffee_ratings.csv")
# print(df.columns)