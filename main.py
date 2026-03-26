from display_country import analysis 
# TODO: import DataCleaner.py to clean up db

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
import numpy as np

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def show_dataframe(df, tree):
    # Clear previous
    tree.delete(*tree.get_children())
    tree["columns"] = list(df.columns)

    # Set headings and column widths (auto-size to header)
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col,
                    #width=max(100, font.Font().measure(col) + 20),
                    anchor="w")

    # Insert rows (convert all values to strings)
    for _, row in df.iterrows():
        values = ["" if pd.isna(v) else str(v) for v in row.tolist()]
        tree.insert("", "end", values=values)

    # Adjust column widths to fit contents (optional, may be slow for large files)
    for col in df.columns:
        max_width = 20 #font.Font().measure(col)
        for child in tree.get_children():
            cell_text = tree.set(child, col)
            max_width = 20 #max(max_width, font.Font().measure(cell_text))
        tree.column(col, width=max_width + 20)

def open_file_and_show(tree):
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if not path:
        return
    try:
        df = pd.read_csv(path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV:\n{e}")
        return
    show_dataframe(df, tree)

def process_number(new_N: int):
    top_N = new_N
    print("Calculating results. . . ")
    results = analysis(df, top_N)

    # Display the top 5 countries and their calculated scores
    print(f"--- Top {top_N} Recommended Countries ---")
    print(results[['final_score', 'producer_count', 'flavor', 'aroma', 'body', 'uniformity', 'cupper_points', 'aftertaste',
           'acidity', 'balance', 'clean_cup', 'sweetness', 'moisture', 'process_score', 'caffeine_score']])

    # Save the Top N specifically
    results.to_csv(f"top_{top_N}_countries.csv")
    print(f"\nResults successfully saved to 'top_{top_N}_countries.csv'")

    # Open and loads the saved .csv file  
    new_df = pd.read_csv(f"top_{top_N}_countries.csv")
    show_dataframe(new_df, tree) 
    
    # Optional: Access just the #1 recommendation
    best_country = results.index[0]
    print(f"\nThe best country to send the buyer to is: {best_country}")

    # print(results.columns)
    # df = pd.read_csv(r"data/simplified_coffee_ratings.csv")
    # print(df.columns)

def on_submit():
    s = entry.get().strip()
    try:
        val = int(s)
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter an integer.")
        return

    MIN, MAX = 1, 100  # example range
    if not (MIN <= val <= MAX):
        messagebox.showerror("Out of range", f"Enter an integer between {MIN} and {MAX}.")
        return

    process_number(val)  # pass validated int to your function

# TEST: preload a CSV (optional)
df = pd.read_csv(r"data/simplified_coffee_ratings.csv")
# print(df)
top_N = 5 # Default: we look for the top 5 countries

df.columns = df.columns.str.strip().str.lower() # Cleans spaces and matches case

# The main tkinter window
window = tk.Tk()
window.title('CSV Viewer')
window.geometry("900x500")

toolbar = ttk.Frame(window)
toolbar.pack(fill="x", padx=4, pady=4)

# Treeview + scrollbars
tree_frame = tk.Frame(window)
tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

vsb = ttk.Scrollbar(tree_frame, orient="vertical")
hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
tree = ttk.Treeview(tree_frame, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
vsb.config(command=tree.yview)
hsb.config(command=tree.xview)

open_btn = tk.Button(toolbar,
                     text="Open CSV",
                     command=lambda:
                     open_file_and_show(tree)
)
open_btn.pack(side="left")

label = tk.Label(text="Search for top suppliers/countries:")
label.pack(padx=10, pady=(10,0))

entry = tk.Entry()
entry.pack(padx=10, pady=5)
entry.focus_set()

tk.Button(text="Submit", command=on_submit).pack(pady=(0,10))

show_dataframe(df, tree) 

vsb.pack(side="right", fill="y")
hsb.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

window.mainloop()
