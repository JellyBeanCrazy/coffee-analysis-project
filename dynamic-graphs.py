import geopandas as gpd
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)

import tkinter as tk
from tkinter import ttk

# TEST: Loading db
df = pd.read_csv("data/simplified_coffee_ratings.csv")
# print(df)

other_columns = ['species',
                 'owner',
                 'farm_name',
                 'lot_number',
                 'mill',
                 'company',
                 'altitude',
                 'region',
                 'producer',
                 'number_of_bags',
                 'bag_weight',
                 'in_country_partner',
                 'harvest_year',
                 'grading_date',
                 'owner_1',
                 'variety',
                 'processing_method']
worldmap_columns = ['country_of_origin']
histogram_columns = ['aroma',
                     'flavor',
                     'aftertaste',
                     'acidity',
                     'body',
                     'balance',
                     'uniformity',
                     'clean_cup',
                     'sweetness',
                     'cupper_points',
                     'moisture']
figure_columns = worldmap_columns + histogram_columns

def histogram(data,
              col,
              bins=100,
              figsize=(5,4),
              dpi=100):
    fig = Figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)
    ax.hist(data, bins=bins, color="#4C72C0", edgecolor="black", alpha=0.8)
    ax.set_title(f"Distribution of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Count")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    return fig

def worldmap(df,
             figsize=(6, 4),
             dpi=200):
    # Load world countries from URL (no geodatasets needed)
    world_map = gpd.read_file(
        "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    )
    #print(world_map)
    #print(world_map.columns.tolist())
    #print(sorted(world_map['NAME'].unique()))
    
    def normalize_name(s): # Normalize names for better matching
        return (
            str(s)
            .strip()
            .replace("United States (Hawaii)", "United States of America")
            .replace("United States (Puerto Rico)", "Puerto Rico")
            .replace("Tanzania, United Republic Of", "Tanzania")
            .replace("Cote d?Ivoire", "Côte d'Ivoire")
            .lower()
        )
    # normalize the world names to create a join key
    world_map['key'] = world_map['NAME'].map(lambda x: normalize_name(x))
    df = df.copy() # CIA safety
    df['country_key'] = df['country_of_origin'].map(lambda x: normalize_name(x))
    counts = df["country_key"].value_counts()               # absolute
    norm_counts = df["country_key"].value_counts(normalize=True)  # relative
    #print(counts)
    #print(norm_counts)
    
    # convert counts to DataFrame for merging
    counts_df = counts.rename_axis("key").reset_index(name="count")
    norm_counts_df = norm_counts.rename_axis("key").reset_index(name="proportion")
    merged = world_map.merge(counts_df, on='key', how='left')
    merged = merged.merge(norm_counts_df, on='key', how='left')
    merged['count'] = merged['count'].fillna(0).astype(int)
    merged['proportion'] = merged['proportion'].fillna(0.0)
    
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    merged.plot(
        column='count',  # 'count' or 'proportion'
        cmap='Reds',
        legend=True,
        ax=ax,
        edgecolor='black',
        linewidth=0.2,
        legend_kwds={'shrink': 0.5}
    )

    ax.set_title('World Heatmap')
    ax.set_aspect('equal')   # or 'equal' if you want equal x/y scaling
    ax.axis('off')

    fig.tight_layout()
    return fig

def plot():
    # Clear any previous canvas widgets if desired
    for child in window.winfo_children():
        if isinstance(child, tk.Canvas):
            child.destroy()
            
    # Read combobox variable
    col = n.get() or plotchoosen.get()  
    if not col:
        return

    # Create figure
    if col in histogram_columns:
        data = pd.to_numeric(df[col], errors="coerce").dropna() # Prepare data (e.g. drop NaNs)
        fig = histogram(data, col)
    elif col in worldmap_columns:
        fig = worldmap(df)
    else:
        raise ValueError(f"Unsupported column for charting: {col}")

    # Draw matplotlib figure to Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    #toolbar = NavigationToolbar2Tk(canvas, window)
    #toolbar.update()
    #canvas.get_tk_widget().pack()
    
# The main tkinter window
window = tk.Tk()
window.title('pyplot in Tkinter')
window.geometry("600x600")

# Define a label for the list.  
label = ttk.Label(window, text = "Select graph")
label.pack(pady=5)

n = tk.StringVar()
plotchoosen = ttk.Combobox(window,
                           width = 27,
                           textvariable = n,
                           state="readonly")
plotchoosen['values'] = (figure_columns)
plotchoosen.current(0)
plotchoosen.pack(pady=5)

plot_button = ttk.Button(master = window,
                         command = plot,
                         width = 10,
                         text = "Plot")
plot_button.pack(pady=10)

window.mainloop()
