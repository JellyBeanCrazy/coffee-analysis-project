import pandas as pd
import matplotlib.pyplot as plt
import random
import numpy as np

def supply_calculator(df):
    # 1. Ensure weights are numeric (handles strings like '60 kg' by stripping non-digits)
    if df['bag_weight'].dtype == 'object':
        df['bag_weight_numeric'] = df['bag_weight'].str.extract('(\d+)').astype(float)
    else:
        df['bag_weight_numeric'] = df['bag_weight']

    # 2. Calculate total weight per row
    df['total_supply_kg'] = df['number_of_bags'] * df['bag_weight_numeric']

    # 3. How much each COUNTRY supplies
    country_supply = df.groupby('country_of_origin')['total_supply_kg'].sum()

    # 4. How much each PRODUCER supplies (Global total)
    producer_supply = df.groupby('producer')['total_supply_kg'].sum()

    # 5. How much each PRODUCER supplies per COUNTRY
    # This identifies producers operating in multiple regions
    producer_per_country = df.groupby(['country_of_origin', 'producer'])['total_supply_kg'].sum()

    return {
        "by_country": country_supply.sort_values(ascending=False),
        "by_producer": producer_supply.sort_values(ascending=False),
        "producer_breakdown": producer_per_country.sort_values(ascending=False)
    }