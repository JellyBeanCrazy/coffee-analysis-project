import pandas

df = pandas.read_csv('data/simplified_coffee_ratings.csv')

# Drop any rows that do not have a country
df.dropna(subset=["country_of_origin","species"],inplace=True)

# Convert all bag_weight in pounds to kgs and remove string
weights = df["bag_weight"]
for weight in weights:
    pounds = False
    str_len = len(weight)
    weight_ints = ""
    for char in weight:
        if char in "lbs":
            pounds = True
        if char.is_integer():
            weight_ints += char
    weight_value = float(weight_ints)
    if pounds:
        weight = int(weight_value/2.2)
    else:
        weight = int(weight_value)

# List of columns with number values
int_cols = ["number_of_bags", "bag_weight", "aroma", "flavor","aftertaste","acidity","body","balance","uniformity","clean_cup","sweetness","cupper_points","moisture"]
# Get mean of each column and replace any empty values with it
for col_name in int_cols:
    mean = df[col_name].mean()
    df.fillna({col_name: mean}, inplace=True)

# List of columns with string values
str_cols = ["owner","farm_name","lot_number","mill","company","region","producer", "in_country_partner", "harvest_year", "grading_date", "owner_1", "variety", "processing_method"]
# Replace empty values with "Unknown" for string columns
for col_name in str_cols:
    df.fillna({col_name: "unknown"}, inplace=True)