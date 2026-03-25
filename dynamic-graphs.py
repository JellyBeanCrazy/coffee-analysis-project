import pandas as pd
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
    
    # Create figure and histogram
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.hist(data, bins=30, color="#4C72B0", edgecolor="black", alpha=0.9)
    ax.set_title(f"Distribution of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Count")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    

    # Draw matplotlib figure to Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    canvas.get_tk_widget().pack()
    
# The main tkinter window
window = tk.Tk()
window.title('pyplot in Tkinter')
window.geometry("600x600")

# Define a label for the list.  
label = ttk.Label(window, text = "Select graph")
label.pack(pady=5)

n = tk.StringVar()
plotchoosen = ttk.Combobox(window, width = 27, textvariable = n)
plotchoosen['values'] = ('aroma',
                         'flavor',
                         'aftertaste',
                         'acidity',
                         'body',
                         'balance',
                         'uniformity',
                         'clean_cup',
                         'sweetness',
                         'cupper_points',
                         'moisture')
plotchoosen.current(0)
plotchoosen.pack(pady=5)

plot_button = ttk.Button(master = window,
                         command = plot,
                         width = 10,
                         text = "Plot")
plot_button.pack(pady=10)


window.mainloop()
