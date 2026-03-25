import pandas

df = pandas.read_csv('data/simplified_coffee_ratings.csv')

# Drop any rows that do not have a country
df.dropna(subset=["country_of_origin","species"],inplace=True)

# Drop lot_number column as more than 70% of the values are missing
df.drop(columns=['lot_number'],inplace=True)

# Get rid of duplicate columns (owner/owner_1) but make sure no gaps are left
df['owner'] = df['owner'].fillna(df['owner_1'])
df.drop(columns=['owner_1'],inplace=True)

# Drop any rows that do not have a country, species or owner
df.dropna(subset=["country_of_origin","species","owner"],inplace=True)

# Get rid of whitespace
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

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
str_cols = ["farm_name","mill","company","region","producer", "in_country_partner", "harvest_year", "grading_date", "variety", "processing_method"]
# Replace empty values with "Unknown" for string columns
for col_name in str_cols:
    df.fillna({col_name: "unknown"}, inplace=True)