import geopandas as gpd
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)

import tkinter as tk
from tkinter import ttk

""" simplified_coffee_ratings.csv COLUMNS
species
owner
country_of_origin
farm_name
lot_number
mill
company
altitude
region
producer
number_of_bags
bag_weight
in_country_partner
harvest_year
grading_date
owner_1
variety
processing_method
aroma
flavor
aftertaste
acidity
body
balance
uniformity
clean_cup
sweetness
cupper_points
moisture           
"""
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

def worldmap(figsize=(6, 4),
             dpi=200):
    # Load world countries from URL (no geodatasets needed)
    world_map = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")

    # Dummy data
    world_map['dummy_score'] = np.random.rand(len(world_map))
    counts = df['country_of_origin'].value_counts()
    norm_counts = df['country_of_origin'].value_counts(normalize=True)
    print(norm_counts)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    world_map.plot(
        column='dummy_score',
        cmap='Reds',
        legend=True,
        ax=ax,
        edgecolor='black',
        linewidth=0.2,
        legend_kwds={'shrink': 0.5}
    )

    ax.set_title('World Heatmap Example')
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

    # Prepare data (e.g. drop NaNs)
    data = pd.to_numeric(df[col], errors="coerce").dropna()
    
    # Create figure
    if col in histogram_columns:
        fig = histogram(data, col)
    elif col in worldmap_columns:
        fig = worldmap()
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
plotchoosen = ttk.Combobox(window, width = 27, textvariable = n, state="readonly")
plotchoosen['values'] = (figure_columns)
plotchoosen.current(0)
plotchoosen.pack(pady=5)

plot_button = ttk.Button(master = window,
                         command = plot,
                         width = 10,
                         text = "Plot")
plot_button.pack(pady=10)


window.mainloop()
