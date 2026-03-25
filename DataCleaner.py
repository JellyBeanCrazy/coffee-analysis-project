import pandas

df = pandas.read_csv('data/simplified_coffee_ratings.csv')

# List of columns with number values
int_cols = ["number_of_bags", "aroma", "flavor","aftertaste","acidity","body","balance","uniformity","clean_cup","sweetness","cupper_points","moisture"]

# Get mean of each column and replace any empty values with it
for col_name in int_cols:
    mean = df[col_name].mean()
    df.fillna({col_name: mean}, inplace=True)

