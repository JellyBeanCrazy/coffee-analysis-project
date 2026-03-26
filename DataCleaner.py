import pandas
import re

def convert_bag_weight(weight):
    """
    Converts a bag weight value into a single number measured in kilograms. 
    Handles cases where the weight is given in pounds by converting it to kg. 
    If the value is missing or contains no recognisable number, it is returned 
    as empty.

    Parameters:
        weight (str): The raw bag weight value from the CSV, for example "60kg" or "132 lbs".

    Returns:
        float: The weight in kilograms, or NA if the value could not be converted.
    """
    if pandas.isna(weight):
        return pandas.NA
    pounds = False
    str_len = len(weight)
    weight_ints = ""
    for char in weight:
        if char in "lbs":
            pounds = True
        if char.is_integer():
            weight_ints += char
    if weight_ints == "":
        return pandas.NA
    weight_value = float(weight_ints)
    if pounds:
        weight_value = int(weight_value/2.2)
    return weight_value


def get_harvest_year(data):
    """
    Extracts a single 4-digit harvest year from a raw value that may be in a 
    variety of formats, for example "2019", "19/20", or "March 2018". If no 
    recognisable year can be found, the value is returned as empty.

    Parameters:
        data: The raw harvest year value from the CSV.

    Returns:
        int: The harvest year as a 4-digit number, or NA if no year could be found.
    """
    if pandas.isna():
        return pandas.NA
    match = re.search(r'\b(19|20)\d{2}\b', str(data))
    if match:
        data = int(match.group)
    else:
        match = re.search(r'\b\d{2})\b', str(data))
        if match:
            data = 2000 + int(match.group())
        else:
            data = pandas.NA
    return data

def parse_altitudes(data):
    """
    Converts a raw altitude value into a single number measured in meters. 
    Handles a wide variety of formats including ranges (e.g. "1500-1700m"), 
    values given in feet, and values given in kilometers. Altitudes that are 
    clearly incorrect (below sea level or above 4000m) are returned as empty 
    as coffee cannot grow at those heights.

    Parameters:
        data: The raw altitude value from the CSV, for example "1500m", "4921 feet", or "1.5km".

    Returns:
        int: The altitude in meters rounded to the nearest whole number, or NA if 
        the value could not be converted or is outside the valid range.
    """
    if pandas.isna(data):
        return pandas.NA
    s = str(data).strip().lower()

    if re.fullmatch(r'[a-z\s]+', s):
        return pandas.NA

    is_feet = bool(re.search(r'\bft\.?|\bfeet\b|\bpies\b|\b\ds*f\b', s))
    s = re.sub(
        r'meters?|metros?|msnm|m\.s\.n\.m\.?|masl|mals?|msnn?|msm|mosl|metres above sea level:'
        r'mts\.?|m\.o\.s\.l\.?|m\.s\.l\.?|psnm|p\.s\.n\.m\.?|psn|'
        r'above|approx\.?|between|and|thru|on average|'
        r'公尺|nivel del mar|sobre el nivel del mar|a\.s\.l\.?|'
        r'feet|ft\.?|pies|\bf\b',
        ' ', s
    )

    s = re.sub(r"'", '', s)
    
    s = re.sub(r'[^\d\.\-\s~]', ' ', s).strip()
    
    numbers = [float(n) for n in re.findall(r'\d+\.?\d*', s)]
    
    if not numbers:
        return pandas.NA
    
    data = sum(numbers) / len(numbers)

    if is_feet:
        data *= 0.3048

    if data < 10:
        data *= 1000
    
    if data > 4000 or data <= 0:
        return pandas.NA
    
    data = round(data)

    return data

def data_cleaning_algo(csv_file_path):
    """
    Runs the full data cleaning process on a coffee ratings CSV file and returns 
    a cleaned version of the data. This includes removing duplicate and unnecessary 
    columns, dropping rows with critical missing values, standardising bag weights 
    and altitudes to consistent units, extracting valid harvest years, and filling 
    in any remaining missing values with either the column average (for numerical 
    columns) or "unknown" (for text columns).

    Parameters:
        csv_file_path (str): The file path to the CSV file to be cleaned, 
        for example "data/simplified_coffee_ratings.csv".

    Returns:
        pd.DataFrame: The cleaned version of the dataset, ready for analysis.
    """
    df = pandas.read_csv(csv_file_path)

    df.drop(columns=['lot_number'],inplace=True)

    df['owner'] = df['owner'].fillna(df['owner_1'])
    df.drop(columns=['owner_1'],inplace=True)

    df.dropna(subset=["country_of_origin","species","owner"],inplace=True)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    df["bag_weight"] = df["bag_weight"].apply(convert_bag_weight)

    quartiles = df["bag_weight"].quantile([0.25,0.75])
    outlier_bound = quartiles[1] + (quartiles[1] - quartiles[0]) * 1.5
    df.loc[df['bag_weight_kg'] > outlier_bound, 'bag_weight_kg'] = pandas.NA

    df["harvest_year"] = df["harvest_year"].apply(get_harvest_year)
    df["altitude"] = df["altitude"].apply(parse_altitudes)

    int_cols = ["number_of_bags", "bag_weight", "altitude", "aroma", "flavor","aftertaste","acidity","body","balance","uniformity","clean_cup","sweetness","cupper_points","moisture"]
    for col_name in int_cols:
        mean = df[col_name].mean()
        df.fillna({col_name: mean}, inplace=True)

    str_cols = ["farm_name","mill","company","region","producer", "in_country_partner", "harvest_year", "grading_date", "variety", "processing_method"]
    for col_name in str_cols:
        df.fillna({col_name: "unknown"}, inplace=True)

    return df