# For processing data
import pandas
# For matching regex of years for harvest_year and altitude ranges
import re

# Convert all bag_weight in pounds to kgs and remove string
def convert_bag_weight(weight):
    if pandas.isna(weight):
        return pandas.NA
    pounds = False
    str_len = len(weight)
    weight_ints = ""
    for char in weight:
        if char in "lbs":
            pounds = True
        if char in "0123456789":
            weight_ints += char
    if weight_ints == "":
        return pandas.NA
    weight_value = float(weight_ints)
    if pounds:
        weight_value = int(weight_value/2.2)
    return weight_value

# Make harvest year into a singular integer year (or NA)
def get_harvest_year(data):
    if pandas.isna(data):
        return pandas.NA
    match = re.search(r'\b(19|20)\d{2}\b', str(data))
    if match:
        data = int(match.group())
    else:
        match = re.search(r'\b\d{2}\b', str(data))
        if match:
            data = 2000 + int(match.group())
        else:
            data = pandas.NA
    return data

# Clean up altitude into a single number measured in meters
def parse_altitudes(data) -> int:
    if pandas.isna(data):
        return pandas.NA
    s = str(data).strip().lower()
    # Random strings that don't contain an altitude
    if re.fullmatch(r'[a-z\s]+', s):
        return pandas.NA
    # Check if it's in feet
    is_feet = bool(re.search(r'\bft\.?|\bfeet\b|\bpies\b|\b\ds*f\b', s))
    # Strip all unit words and stray characters
    s = re.sub(
        r'meters?|metros?|msnm|m\.s\.n\.m\.?|masl|mals?|msnn?|msm|mosl|metres above sea level:'
        r'mts\.?|m\.o\.s\.l\.?|m\.s\.l\.?|psnm|p\.s\.n\.m\.?|psn|'
        r'above|approx\.?|between|and|thru|on average|'
        r'公尺|nivel del mar|sobre el nivel del mar|a\.s\.l\.?|'
        r'feet|ft\.?|pies|\bf\b',
        ' ', s
    )

    # Remove apostrophe/quote used as thousands separator (e.g. 1'500)
    s = re.sub(r"'", '', s)
    
    # Strip leftover non-numeric characters except digits, dot, hyphen, space, tilde
    s = re.sub(r'[^\d\.\-\s~]', ' ', s).strip()
    
    # Extract all numbers
    numbers = [float(n) for n in re.findall(r'\d+\.?\d*', s)]
    
    if not numbers:
        return pandas.NA
    
    # Take midpoint of any range, or the single value
    data = sum(numbers) / len(numbers)

    # Convert feet to m
    if is_feet:
        data *= 0.3048

    # Likely to be km, convert to m
    if data < 10:
        data *= 1000
    
    # Coffee will not grow below sea level, nor will it grow over more than 4000m, these must be outliers
    if data > 4000 or data <= 0:
        return pandas.NA
    
    data = round(data)

    return data

def remove_outliers_iqr(df, column="bag_weight"):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    upper_bound = Q3 + 1.5 * IQR

    filtered_df = df[(df[column] <= upper_bound)]

    return filtered_df

# Runs the algorithm to clean a csv file where a csv file is imported
# This can be used on any csv file in the format of the current coffee-analysis with different data
# To run, from DataCleaner import * then call data_cleaning_algo(<insert csv filepath here>)
def data_cleaning_algo(csv_file_path):
    # Opens the CSV file
    df = pandas.read_csv(csv_file_path)

    # Drop lot_number column as more than 70% of the values are missing
    df.drop(columns=['lot_number'],inplace=True)

    # Get rid of duplicate columns (owner/owner_1) but make sure no gaps are left
    df['owner'] = df['owner'].fillna(df['owner_1'])
    df.drop(columns=['owner_1'],inplace=True)

    # Drop any rows that do not have a country, species or owner
    df.dropna(subset=["country_of_origin","species","owner"],inplace=True)

    # Converts bag_weights to kgs
    df["bag_weight"] = df["bag_weight"].apply(convert_bag_weight)

    # Get rid of outliers
    # df = remove_outliers_iqr(df,"bag_weight")

    # Starts cleaning harvest_year
    df["harvest_year"] = df["harvest_year"].apply(get_harvest_year)

    # Starts cleaning altitude
    df["altitude"] = df["altitude"].apply(parse_altitudes).astype("Int64")

    # List of columns with number values
    int_cols = ["number_of_bags", "bag_weight", "altitude", "aroma", "flavor","aftertaste","acidity","body","balance","uniformity","clean_cup","sweetness","cupper_points","moisture"]
    # Get mean of each column and replace any empty values with it
    for col_name in int_cols:
        mean = df[col_name].mean()
        if (col_name == "altitude"):
            mean = round(mean)
        df.fillna({col_name: mean}, inplace=True)

    # List of columns with string values
    str_cols = ["farm_name","mill","company","region","producer", "in_country_partner", "harvest_year", "grading_date", "variety", "processing_method"]
    # Replace empty values with "Unknown" for string columns
    for col_name in str_cols:
        df.fillna({col_name: "unknown"}, inplace=True)

    return df