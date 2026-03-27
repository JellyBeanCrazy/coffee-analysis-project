from display_country import analysis
import sensitivity_analysis

import geopandas as gpd
import pandas as pd
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)

import DataCleaner
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Define Metric Categories for weighting
primary_quality = ['flavor', 'aroma', 'body', 'uniformity', 'cupper_points']
secondary_quality = ['aftertaste', 'acidity', 'balance',
                     'clean_cup', 'sweetness', 'moisture']
strategic_metrics = ['process_score', 'caffeine_score', 'producer_count']
# Set Default Weights
default_weights = {metric: 1.0 for metric in primary_quality}
default_weights.update({metric: 0.3 for metric in secondary_quality})
default_weights.update({metric: 1.0 for metric in strategic_metrics})

def load_csv_via_datacleaner(path):
    return DataCleaner.data_cleaning_algo(path)

# --- Table Frame (refactor of main.py table parts) ---
class TableFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tree = ttk.Treeview(self, show="headings")
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.df = pd.DataFrame()
        # --- Define controls window ---
        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=6, pady=6)
        # --- Input fields (bottom_left) ---
        left_frame = ttk.Frame(controls)
        left_frame.pack(side="left", padx=6)
        ttk.Button(left_frame, text="Open CSV", command=self.open_file).pack(pady=4)
        ttk.Label(left_frame, text="Search for top suppliers/countries:").pack()
        self.entry = tk.Entry(left_frame)
        self.entry.pack()
        ttk.Button(left_frame, text="Submit", command=self.on_submit).pack(pady=4)
        # --- Weight inputs (bottom_right) ---
        self.weights_frame = ttk.Frame(controls)
        self.weights_frame.pack(side="left", padx=12)
        self.weight_fields = default_weights.copy()
        self.weight_vars = {}
        cols = 5
        n_per_col = (len(self.weight_fields) + cols - 1) // cols
        for idx, name in enumerate(self.weight_fields):
            col = idx // n_per_col
            row = idx % n_per_col
            ttk.Label(self.weights_frame, text=f"{name}:").grid(row=row, column=col*2, sticky="e", padx=(0,6), pady=2)
            var = tk.StringVar(value=str(self.weight_fields[name]))
            ttk.Entry(self.weights_frame, textvariable=var, width=8).grid(row=row, column=col*2+1, sticky="w", pady=2)
            self.weight_vars[name] = var

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            df = load_csv_via_datacleaner(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV:\n{e}")
            return
        df.columns = df.columns.str.strip().str.lower()
        self.df = df
        self.show_dataframe(df)
        
    def show_dataframe(self, df):
        tree = self.tree
        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="w")
        for _, row in df.iterrows():
            values = ["" if pd.isna(v) else str(v) for v in row.tolist()]
            tree.insert("", "end", values=values)

    def read_weights(self):
        weights = {}
        for name, var in self.weight_vars.items():
            s = var.get().strip()
            try:
                val = float(s)
            except ValueError:
                val = self.weight_fields[name]
            weights[name] = val
        return weights

    def on_submit(self):
        s = self.entry.get().strip()
        try:
            val = int(s)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter an integer.")
            return
        if not (1 <= val <= 100):
            messagebox.showerror("Out of range", "Enter an integer between 1 and 100.")
            return
        weights = self.read_weights()
        self.process_number(val, weights)

    def process_number(self, new_N, weights):
        if self.df.empty:
            messagebox.showerror("No data", "Load a CSV first.")
            return
        results = analysis(self.df, new_N, manual_adjustments=False, custom_weights_dict=weights)
        results.to_csv(f"top_{new_N}_countries.csv")
        new_df = pd.read_csv(f"top_{new_N}_countries.csv")
        self.df = new_df
        self.show_dataframe(new_df)
        best_country = results.index[0] if len(results) else "N/A"
        messagebox.showinfo("Done", f"Top {new_N} saved. Best country: {best_country}")

# --- Graph Frame (refactor of dynamic-graphs.py) ---
class GraphFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Load dataset (initial)
        try:
            self.df = DataCleaner.data_cleaning_algo(
                "data/simplified_coffee_ratings.csv"
                )
        except Exception:
            self.df = pd.DataFrame()
        # Controls row
        top = ttk.Frame(self)
        top.pack(fill="x", padx=6, pady=6)
        ttk.Button(top, text="Open CSV", command=self.open_file).pack(side="left", padx=8)
        ttk.Label(top, text="Graphs:").pack(side="left")
        self.plot_type = tk.StringVar()
        self.plot_choosen = ttk.Combobox(top, width=20, textvariable=self.plot_type, state="readonly")
        self.plot_choosen['values'] = ('World Heat Map', 'Histogram',
                                       'Bar Chart', 'Scatter Plot')
        self.plot_choosen.current(0)
        self.plot_choosen.pack(side="left", padx=8)
        ttk.Label(top, text="Statistics:").pack(side="left")
        self.stat_var = tk.StringVar()
        self.stat_combo = ttk.Combobox(top, width=30, textvariable=self.stat_var, state="readonly")
        self.stat_combo.pack(side="left", padx=6)
        self.plot_choosen.bind('<<ComboboxSelected>>', self.update_statistic_values)
        ttk.Button(top, text="Plot", command=self.plot).pack(side="left", padx=8)
        self.canvas_holder = ttk.Frame(self)
        self.canvas_holder.pack(fill="both", expand=True)
        self.histogram_columns = ['aroma','flavor',
                                  'aftertaste','acidity',
                                  'body','balance',
                                  'uniformity','clean_cup',
                                  'sweetness','cupper_points',
                                  'moisture']
        self.worldmap_columns = ['country_of_origin']
        self.bar_columns = ['species','variety',
                            'processing_method']
        self.scatter_columns = [f"{a} vs. {b}"
                                for i,a in enumerate(self.histogram_columns) for b in self.histogram_columns[i+1:]]
        self.update_statistic_values()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            df = load_csv_via_datacleaner(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV:\n{e}")
            return
        self.df = df
        messagebox.showinfo("Loaded", "CSV loaded for plotting.")

    def update_statistic_values(self, *_):
        selected = self.plot_type.get()
        if selected == 'World Heat Map':
            values = self.worldmap_columns
        elif selected == 'Histogram':
            values = self.histogram_columns
        elif selected == 'Bar Chart':
            values = self.bar_columns
        elif selected == 'Scatter Plot':
            values = self.scatter_columns
        else:
            values = []
        self.stat_combo['values'] = values
        if values:
            self.stat_var.set(values[0])
        else:
            self.stat_var.set("")

    # Plotting helper function(S)
    def histogram(self, data, col, bins=50, figsize=(6,4), dpi=100, color="#4C72C0"):
        fig = Figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)
        ax.hist(data, bins=bins, color=color, edgecolor="black", alpha=0.8)
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        return fig

    def bar_chart(self, data, col, top_n=10, figsize=(6,4), dpi=100, color="#4C72C0"):
        counts = data[col].fillna("Missing").astype(str).value_counts()
        if top_n is not None and top_n < len(counts):
            top = counts.iloc[:top_n]
            other = counts.iloc[top_n:].sum()
            counts = top.append(pd.Series({"Other": other}))
        fig = Figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)
        labels = counts.index.astype(str)
        values = counts.values
        ax.bar(labels, values, color=color, edgecolor="black", alpha=0.9)
        ax.set_title(f"Counts of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=30, labelsize=8)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        return fig

    def scatter(self, df, x_col, y_col, figsize=(6,4), dpi=100, color="#4C72C0", alpha=0.7, size=20):
        fig = Figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)
        x = pd.to_numeric(df[x_col], errors="coerce")
        y = pd.to_numeric(df[y_col], errors="coerce")
        mask = x.notna() & y.notna()
        ax.scatter(x[mask], y[mask], c=color, alpha=alpha, s=size, edgecolor="black", linewidth=0.2)
        ax.set_title(f"{x_col} vs. {y_col}")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        return fig

    def worldmap(self, df, figsize=(8,5), dpi=100):
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
        world_map = gpd.read_file(
            "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
            )
        def normalize_name(s):
            return (str(s)
                    .strip()
                    .replace("United States (Hawaii)", "United States of America")
                    .replace("United States (Puerto Rico)", "Puerto Rico")
                    .replace("Tanzania, United Republic Of", "Tanzania")
                    .replace("Cote d?Ivoire", "Côte d'Ivoire")
                    .lower()
                    )
        # Normalize the world names to create a join key
        world_map['key'] = world_map['NAME'].map(lambda x: normalize_name(x))
        df = df.copy()# CIA safety
        df['country_key'] = df['country_of_origin'].map(lambda x: normalize_name(x))
        counts = df["country_key"].value_counts() # Absolute
        norm_counts = df["country_key"].value_counts(normalize=True) # Relative
        # Convert counts to DataFrame for merging
        counts_df = counts.rename_axis("key").reset_index(name="count")
        norm_counts_df = norm_counts.rename_axis("key").reset_index(name="proportion")
        merged = world_map.merge(counts_df, on='key', how='left').merge(norm_counts_df, on='key', how='left')
        merged['count'] = merged['count'].fillna(0).astype(int)
        merged['proportion'] = merged['proportion'].fillna(0.0)
        fig = Figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)
        merged.plot(
            column='count',
            cmap='Reds',
            legend=True,
            ax=ax,
            edgecolor='black',
            linewidth=0.2,
            legend_kwds={'shrink': 0.5}
        )
        ax.set_title('World Heatmap')
        ax.set_aspect('equal')
        ax.axis('off')
        fig.tight_layout()
        return fig

    def parse_pair(self, pair_str):
        left, sep, right = pair_str.partition(" vs. ")
        if sep == "":
            left, sep, right = pair_str.partition(" vs ")
        return left.strip(), right.strip()

    def clear_canvas_holder(self):
        for child in self.canvas_holder.winfo_children():
            child.destroy()

    def plot(self):
        """
        Reads the column selected by the user from the dropdown menu and generates 
        the appropriate chart for that column. If the selected column is a quality 
        measure such as aroma or flavour, a histogram is shown. If the selected 
        column is country of origin, a world heatmap is shown. The chart is then 
        displayed inside the application window.
        """
        self.clear_canvas_holder()
        plot_type = self.plot_type.get() # Read combobox variable
        col = self.stat_var.get()
        if not col:
            return
        if plot_type == "Histogram":
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            fig = self.histogram(data, col, dpi=150)
        elif plot_type == "Bar Chart":
            fig = self.bar_chart(self.df, col, top_n=None, figsize=(8,5), dpi=80)
        elif plot_type == "World Heat Map":
            fig = self.worldmap(self.df, dpi=150)
        elif plot_type == "Scatter Plot":
            x_col, y_col = self.parse_pair(col)
            fig = self.scatter(self.df, x_col, y_col)
        else:
            return
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

# --- Sensitivity Frame (refactor of sensitivity_analysis.py) ---
class SensitivityFrame(ttk.Frame):
    def __init__(self, parent, get_df_callback):
        # Load dataset (initial)
        try:
            self.df = DataCleaner.data_cleaning_algo(
                "data/simplified_coffee_ratings.csv"
                )
        except Exception:
            self.df = pd.DataFrame()
            
        super().__init__(parent)
        self.get_df = get_df_callback

        # Controls row
        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=6, pady=6)
        ttk.Button(controls, text="Open CSV", command=self.open_file).pack(side="left", padx=8)
        ttk.Label(controls, text="Iterations:").pack(side="left", padx=(0,6))
        self.iter_var = tk.IntVar(value=50)
        ttk.Entry(controls, textvariable=self.iter_var, width=6).pack(side="left")

        """
        self.terminal_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Use terminal prompts", variable=self.terminal_var).pack(side="left", padx=8)
        """
        # Sensitivity weight ranges
        self.metrics = ['flavor','aroma','body','uniformity','cupper_points',
                'aftertaste','acidity','balance','clean_cup','sweetness',
                'moisture','process_score','caffeine_score','producer_count']
        self.range_vars = {}  # {metric: (min_var, max_var)}

        ranges_frame = ttk.LabelFrame(self, text="Weight Ranges")
        ranges_frame.pack(fill="x", padx=6, pady=6)

        cols = 4
        rows = (len(self.metrics) + cols - 1) // cols
        for idx, m in enumerate(self.metrics):
            col = idx // rows
            row = idx % rows
            lbl = ttk.Label(ranges_frame, text=m)
            lbl.grid(row=row*2, column=col*2, sticky="w", padx=4, pady=(4,0))
            min_var = tk.StringVar(value="0.5")
            max_var = tk.StringVar(value="1.5")
            ttk.Label(ranges_frame, text="Min").grid(row=row*2+1, column=col*2, sticky="e")
            ttk.Entry(ranges_frame, textvariable=min_var, width=6).grid(row=row*2+1, column=col*2+1, sticky="w", padx=(2,8))
            ttk.Label(ranges_frame, text="Max").grid(row=row*2+1, column=col*2+2, sticky="e")
            ttk.Entry(ranges_frame, textvariable=max_var, width=6).grid(row=row*2+1, column=col*2+3, sticky="w", padx=(2,8))
            self.range_vars[m] = (min_var, max_var)

        ttk.Button(controls, text="Run Sensitivity Sweep", command=self.run).pack(side="left", padx=8)
        ttk.Button(controls, text="Save Plot", command=self.save_plot).pack(side="left")
        
        # RESULTS: treeview + canvas
        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=6, pady=6)
        # left pane: treeview with vertical scrollbar
        left_pane = ttk.Frame(paned)
        left_pane.pack(fill="both", expand=True)
        vsb = ttk.Scrollbar(left_pane, orient="vertical")
        self.result_tree = ttk.Treeview(left_pane,
                                        columns=("avg_score",),
                                        show="headings",
                                        yscrollcommand=vsb.set)
        vsb.config(command=self.result_tree.yview)
        self.result_tree.heading("avg_score", text="avg_score")
        self.result_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        # right pane: canvas holder for matplotlib figure
        right_pane = ttk.Frame(paned)
        right_pane.pack(fill="both", expand=True)
        self.canvas_holder = ttk.Frame(right_pane)
        self.canvas_holder.pack(fill="both", expand=True)
        # add panes to panedwindow and set relative weights
        paned.add(left_pane, weight=1)
        paned.add(right_pane, weight=3)

        self.latest_result_df = None

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            df = load_csv_via_datacleaner(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV:\n{e}")
            return
        df.columns = df.columns.str.strip().str.lower()
        self.df = df
        self.show_dataframe(df)
        messagebox.showinfo("Loaded", "CSV loaded for sensitivity analysis.")
    def collect_ranges_from_ui(self):
        ranges = {}
        for m, (min_var, max_var) in self.range_vars.items():
            try:
                low = float(min_var.get())
            except ValueError:
                low = 0.5
            try:
                high = float(max_var.get())
            except ValueError:
                high = 1.5
            if high < low:
                low, high = high, low
            ranges[m] = (low, high)
        return ranges

    def run(self):
        df = self.get_df()
        if df is None or df.empty:
            messagebox.showerror("No data", "Load a CSV first (in Table tab).")
            return
        iterations = max(1, int(self.iter_var.get()))
        #use_terminal = bool(self.terminal_var.get()) #TODO: add condional block
        self.result_tree.delete(*self.result_tree.get_children())
        ranges = self.collect_ranges_from_ui()
        try:
            result_df = sensitivity_analysis.run_parameter_sweep(
                df.copy(),
                iterations=iterations,
                ranges=ranges,
                interactive=False
                )
        except Exception as e:
            messagebox.showerror("Error", f"Sweep failed:\n{e}")
            return
        # -- Store & Show --
        self.latest_result_df = result_df
        # show top 10 in tree
        self.result_tree["columns"] = list(result_df.columns)
        for col in result_df.columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=120, anchor="w")
        for idx, row in result_df.iterrows():
            vals = ["" if pd.isna(v) else str(v) for v in row.tolist()]
            self.result_tree.insert("", "end", values=vals)

        # render matplotlib plot from plot_results (it uses plt.show/save). We'll produce a Figure and embed it instead:
        try:
            # Sensitivity module returns a DataFrame; reuse its plotting function but instead create a Figure here
            fig = sensitivity_analysis._build_plot_figure(result_df) if hasattr(sensitivity_analysis, "_build_plot_figure") else None
        except Exception:
            fig = None

        # If module doesn't expose a Figure builder, fallback to making a simple bar plot here:
        if fig is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8,4))
            score_col = result_df.columns[0]
            result_df[score_col].plot(kind="bar", ax=ax, color="skyblue", edgecolor="navy")
            ax.set_title("Stability Analysis: Average Country Scores")
            ax.set_ylabel("Average Final Score")
            ax.set_xticklabels(result_df.index, rotation=45, ha='right')
            fig.tight_layout()

        # embed figure
        for child in self.canvas_holder.winfo_children():
            child.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._current_fig = fig

    def save_plot(self):
        if getattr(self, "_current_fig", None) is None:
            messagebox.showinfo("No plot", "Run the sweep first.")
            return
        path = ttk.filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png"),("All files","*.*")])
        if not path:
            return
        self._current_fig.savefig(path)
        messagebox.showinfo("Saved", f"Plot saved to {path}")

# --- Main App with Notebook ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Coffee Analysis — Table & Graphs")
        self.geometry("1000x700")
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self.table_tab = TableFrame(nb)
        self.graph_tab = GraphFrame(nb)
        self.sensitivity_tab = SensitivityFrame(nb, get_df_callback=lambda: self.table_tab.df)
        nb.add(self.table_tab, text="Table")
        nb.add(self.graph_tab, text="Graphs")
        nb.add(self.sensitivity_tab, text="Sensitivity")

if __name__ == "__main__":
    app = App()
    app.mainloop()
