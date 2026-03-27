from display_country import analysis 

import geopandas as gpd
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
import numpy as np

import DataCleaner

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Define Metric Categories for weighting
primary_quality = ['flavor', 'aroma', 'body', 'uniformity', 'cupper_points']
secondary_quality = ['aftertaste', 'acidity', 'balance',
                     'clean_cup','sweetness', 'moisture']
strategic_metrics = ['process_score', 'caffeine_score', 'producer_count']
# Set Default Weights
weights = {metric: 1.0 for metric in primary_quality}
weights.update({metric: 0.3 for metric in secondary_quality})
weights.update({metric: 1.0 for metric in strategic_metrics})

def show_dataframe(df, tree):
    """
    Displays the contents of a DataFrame (a table of data) in the application window.
    The data is shown in a scrollable table format on screen, where each column from 
    the DataFrame becomes a column in the table, and each row of data is inserted as 
    a new row in the table.

    Parameters:
    df (pd.DataFrame): The table of data to display, for example the coffee ratings CSV.
    tree (ttk.Treeview): The visual table element in the application window that 
    the data gets loaded into.
    """
    tree.delete(*tree.get_children())
    tree["columns"] = list(df.columns)

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col,
                    anchor="w")

    for _, row in df.iterrows():
        values = ["" if pd.isna(v) else str(v) for v in row.tolist()]
        tree.insert("", "end", values=values)

    for col in df.columns:
        max_width = 20
        for child in tree.get_children():
            cell_text = tree.set(child, col)
            max_width = 20
        tree.column(col, width=max_width + 20)


def open_file_and_show(tree):
    """
    Opens a file browser window allowing the user to select a CSV file from 
    their computer. Once a file is selected, it's read in as a table of data 
    and displayed in the application window. If the file cannot be read, an 
    error message is shown to the user.

    Parameters:
    tree (ttk.Treeview): The visual table element in the application window 
    that the data gets loaded into.
    """
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if not path:
        return
    try:
        df = DataCleaner.data_cleaning_algo(path)
        # df = pd.read_csv(path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV:\n{e}")
        return
    show_dataframe(df, tree)


def process_number(new_N: int, weights: dict):
    """
    Takes the number entered by the user and finds the top N recommended 
    countries to source coffee from based on the analysis. The results are 
    displayed in the application window, printed to the terminal, and saved 
    as a new CSV file. Also prints the single best country recommendation 
    to the terminal.

    Parameters:
    new_N (int): The number of top countries to find and display, 
    for example entering 5 would return the top 5 recommended countries.
    """
    top_N = new_N
    print("Calculating results. . . ")
    results = analysis(df, top_N, manual_adjustments=False, custom_weights_dict=weights)

    print(f"--- Top {top_N} Recommended Countries ---")
    print(results[['final_score', 'producer_count', 'flavor', 'aroma', 'body', 'uniformity', 'cupper_points', 'aftertaste',
           'acidity', 'balance', 'clean_cup', 'sweetness', 'moisture', 'process_score', 'caffeine_score']])

    results.to_csv(f"top_{top_N}_countries.csv")
    print(f"\nResults successfully saved to 'top_{top_N}_countries.csv'")

    new_df = pd.read_csv(f"top_{top_N}_countries.csv")
    show_dataframe(new_df, tree) 
    
    best_country = results.index[0]
    print(f"\nThe best country to send the buyer to is: {best_country}")

def read_weights(): # on_submit() reads these and calls analysis
    weights = {}
    for name, var in weight_vars.items():
        s = var.get().strip()
        try:
            val = float(s)
        except ValueError:
            val = weight_fields[name]   # fallback to default
        weights[name] = val
    return weights

def on_submit():
    """
    Handles what happens when the user clicks the Submit button. Checks that 
    the value entered is a whole number between 1 and 100. If not, an error 
    message is shown. If the input is valid, it passes the number to 
    process_number() to run the analysis.
    """
    s = entry.get().strip()
    try:
        val = int(s)
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter an integer.")
        return

    MIN, MAX = 1, 100
    if not (MIN <= val <= MAX):
        messagebox.showerror("Out of range", f"Enter an integer between {MIN} and {MAX}.")
        return
    weights = read_weights()
    process_number(new_N=val, weights=weights)

# TEST: preload a CSV (optional)
df = DataCleaner.data_cleaning_algo("data/simplified_coffee_ratings.csv")
# print(df)
top_N = 5 # Default: we look for the top 5 countries

df.columns = df.columns.str.strip().str.lower() # Cleans spaces and matches case

df.columns = df.columns.str.strip().str.lower()

# --- Window setup ---
window = tk.Tk()
window.title('Coffee Analysis Application Ltd.')
window.geometry("900x600")
# --- Toolbar ---
toolbar = ttk.Frame(window)
toolbar.pack(fill="x", padx=4, pady=4)
# --- Load/Open CSV button ---
open_btn = tk.Button(toolbar,
                     text="Open CSV",
                     command=lambda:
                     open_file_and_show(tree)
)
open_btn.pack(side="left")
# --- Table with scrollbars ---
tree_frame = tk.Frame(window)
tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

vsb = ttk.Scrollbar(tree_frame, orient="vertical")
hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
tree = ttk.Treeview(tree_frame,
                    show="headings",
                    yscrollcommand=vsb.set,
                    xscrollcommand=hsb.set)
vsb.config(command=tree.yview)
hsb.config(command=tree.xview)

vsb.pack(side="right", fill="y")
hsb.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)
# --- Define controls window ---
controls = ttk.Frame(window)
controls.pack(fill="x", padx=8, pady=8)
# --- Input fields (bottom_left) ---
left_frame = ttk.Frame(controls)
left_frame.pack(side="left", fill="y", padx=10, pady=10)
tk.Label(left_frame,
         text="Search for top suppliers/countries:"
).pack(padx=10, pady=(0,5))
entry = tk.Entry(left_frame)
entry.pack(padx=10, pady=(0,10))
entry.focus_set()

tk.Button(left_frame,
          text="Submit",
          command=on_submit
).pack(padx=10, pady=(0,10))
# --- Weight inputs (bottom_right) ---
weights_frame = ttk.Frame(controls)
weights_frame.pack(side="left", fill="y", padx=10, pady=10)
weight_fields = weights # Defined default weights at SOF
cols = 5
weight_vars = {}
for idx, name in enumerate(weight_fields):
    col = idx // ((len(weight_fields) + cols - 1) // cols)
    row = idx % ((len(weight_fields) + cols - 1) // cols)  
    ttk.Label(weights_frame, text=f"{name}:").grid(row=row, column=col*2, sticky="e", padx=(0,6), pady=2)
    var = tk.StringVar(value=str(weight_fields[name]))
    ttk.Entry(weights_frame, textvariable=var, width=8).grid(row=row, column=col*2+1, sticky="w", pady=2)
    weight_vars[name] = var
# --- Show initial dataframe ---
show_dataframe(df, tree) 
window.mainloop()
