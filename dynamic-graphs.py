import geopandas as gpd
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)

import tkinter as tk
from tkinter import ttk

import DataCleaner

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
df = DataCleaner.data_cleaning_algo("data/simplified_coffee_ratings.csv")
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
    """
    Creates a histogram chart for a given column of data. A histogram shows 
    how frequently different values appear — for example, how many coffees 
    scored between 7 and 8 for aroma. The bars are grouped into ranges, and 
    the taller the bar, the more coffees fall within that range.

    Parameters:
        data: The column of numerical data to plot.
        col (str): The name of the column, used as the chart title and x-axis label.
        bins (int): The number of bars to divide the data into. Default is 100.
        figsize (tuple): The width and height of the chart in inches. Default is (5, 4).
        dpi (int): The resolution of the chart. Default is 100.
    """
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
    """
    Creates a world heatmap where each country is shaded based on a score.
    The darker the colour, the higher the value for that country. Currently 
    uses dummy/random data as a placeholder until the real coffee data is 
    ready to be plugged in.

    Parameters:
        figsize (tuple): The width and height of the chart in inches. Default is (6, 4).
        dpi (int): The resolution of the chart. Default is 200.
    """
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
    """
    Reads the column selected by the user from the dropdown menu and generates 
    the appropriate chart for that column. If the selected column is a quality 
    measure such as aroma or flavour, a histogram is shown. If the selected 
    column is country of origin, a world heatmap is shown. The chart is then 
    displayed inside the application window.
    """
    for child in window.winfo_children():
        if isinstance(child, tk.Canvas):
            child.destroy()
            
    col = n.get() or plotchoosen.get()  
    if not col:
        return

    data = pd.to_numeric(df[col], errors="coerce").dropna()
    
    if col in histogram_columns:
        fig = histogram(data, col)
    elif col in worldmap_columns:
        fig = worldmap()
    else:
        raise ValueError(f"Unsupported column for charting: {col}")

    canvas = FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
    canvas.get_tk_widget().pack()
    
window = tk.Tk()
window.title('pyplot in Tkinter')
window.geometry("600x600")

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
