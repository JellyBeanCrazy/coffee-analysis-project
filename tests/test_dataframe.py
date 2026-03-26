import pytest
import pandas as pd
from supply_analysis import supply_calculator


def test_supply_calculator_math():
    # 1. Create a "Mock" DataFrame (minimal data)
    data = {
        'country_of_origin': ['Ethiopia', 'Ethiopia'],
        'producer': ['Estate A', 'Estate A'],
        'number_of_bags': [10, 5],
        'bag_weight': ['60 kg', '60 kg']
    }
    df = pd.DataFrame(data)

    # 2. Run your function
    results = supply_calculator(df)

    # 3. Assert (Check if (10+5) * 60 = 900)
    # Accessing the 'by_country' Series from your dictionary
    total_ethiopia = results['by_country']['Ethiopia']
    
    assert total_ethiopia == 900
    assert "by_producer" in results

def test_monte_carlo_output_shape(sample_df):
    from sensitivity_analysis import run_parameter_sweep
    
    # Run a tiny version of your simulation (2 iterations)
    # Use a mock input to bypass the 'input()' prompts if necessary
    results = run_parameter_sweep(sample_df, iterations=2)
    
    # Check that it returns a DataFrame with at most 10 rows
    assert isinstance(results, pd.DataFrame)
    assert len(results) <= 10
    assert 'avg_score' in results.columns