# ------ Description of graphs -------
# SCATTER PLOT
import matplotlib.pyplot as plt
import numpy as np

# This is just a random scatter plot to show how to read it, not based on the actual data
x = np.random.rand(50)
y = np.random.rand(50)

plt.scatter(x, y)
plt.title("Scatter Plot")
# No real axis labels yet, just a description explaining what a scatter plot shows
plt.figtext(0.5, 0.01, 
    "If the variables are related, the points will form a pattern. If they aren't "
    "related, the points will be randomly scattered. If as the value of the x variable "
    "increases, the value of the y variable also increases, then there is a positive "
    "correlation. If as the value of the x variable increases, the value of the y "
    "variable decreases, then there is a negative correlation.",
    ha="center", wrap=True)
plt.show()



# BAR CHART

# Random data
x = ['A', 'B', 'C', 'D', 'E']
y = np.random.randint(1, 100, 5)

plt.bar(x, y)
plt.title("Bar Chart")
# No real axis labels yet
plt.figtext(0.5, 0.01,
    "Each bar represents a category. The height of the bar shows the value for that "
    "category. The taller the bar, the higher the value. Comparing bar heights allows "
    "you to see which categories are the highest or lowest.",
    ha="center", wrap=True)
plt.show()



# PIE CHART

# Random data
labels = ['A', 'B', 'C', 'D', 'E']
sizes = np.random.randint(1, 100, 5)

plt.pie(sizes, labels=labels, autopct='%1.1f%%')
plt.title("Pie Chart")
# No real axis labels yet
plt.figtext(0.5, 0.01,
    "Each slice represents a category. The bigger the slice, the larger that category's "
    "share of the total. The percentage shown on each slice tells you exactly what "
    "proportion of the whole that category makes up. All slices together always add up to 100%.",
    ha="center", wrap=True)
plt.show()



# RADAR CHART
import numpy as np
import matplotlib.pyplot as plt

# Random data
categories = ['A', 'B', 'C', 'D', 'E']
values = np.random.randint(1, 10, 5).tolist()

# Need to repeat the first value to close the shape
values += values[:1]
angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]

ax = plt.subplot(111, polar=True)
ax.plot(angles, values)
ax.fill(angles, values, alpha=0.25)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
plt.title("Radar Chart")
plt.figtext(0.5, 0.01,
    "Each spoke represents a different category. The further a point is from the centre, "
    "the higher the value for that category. The shaded shape connects all the values."
    " A larger shaded area overall means higher values across all categories.",
    ha="center", wrap=True)
plt.show()



# HEATMAP
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# Load world countries from URL (no geodatasets needed)
world_map = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")

# Dummy data
world_map['dummy_score'] = np.random.rand(len(world_map))

fig, ax = plt.subplots(figsize=(8, 4))

world_map.plot(ax=ax, column='dummy_score', cmap='Reds', legend=True,
               edgecolor='black', linewidth=0.5)

plt.title('World Heatmap Example')
plt.axis("off")
plt.figtext(0.5, 0.01,
    "Each country is shaded based on its score. The darker the colour, the higher "
    "the value for that country. Grey countries have no data available.",
    ha="center", wrap=True)
plt.show()