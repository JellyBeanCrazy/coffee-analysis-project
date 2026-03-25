import geodatasets
import geopandas as gpd
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import turtle

"""
https://readmedium.com/how-to-make-maps-with-python-part-1-plot-the-world-with-geopandas-d099d98566d1

To create a world heatmap in Python, you'll need to install the geodatasets from the GeoPandas library,
this contains a ton of geographical datasets.

pip install geopandas matplotlib

print(geodatasets.data.flatten().keys())
"""

world_map_file = geodatasets.get_path("naturalearthland")
world_map = gpd.read_file(world_map_file)
# print(world_map)
# print(world_map.columns)
# inspect to find the country name column e.g 'featurecla', 'geometry'

fig, ax = plt.subplots(figsize=(8, 4))

world_map.plot(ax=ax, color='lightgray', edgecolor='none')
world_map.boundary.plot(ax=ax,  edgecolor='black', linewidth=1)

plt.title('World Heatmap Example')
plt.axis("off")
plt.show()



