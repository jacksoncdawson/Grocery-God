import os, sys
import pandas as pd
import unittest
from cleaner import clean_data, old_clean_data

class TestCleaningFunctions(unittest.TestCase):
  def test_compare_clean_implementations(self):
    # Check if the test data file exists
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weeklyad_2025-03-05.csv')
    if not os.path.exists(file_path):
      self.skipTest(f"Test data file {file_path} not found")
      
    # Clean using both functions
    new_cleaned = clean_data(file_path)
    old_cleaned = old_clean_data(file_path)
    
    # Save both dataframes to CSV for manual inspection
    new_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'new_cleaned_output.csv')
    old_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'old_cleaned_output.csv')
    
    new_cleaned.to_csv(new_output_path, index=True)
    old_cleaned.to_csv(old_output_path, index=True)
    
    print(f"\n=== CSV FILES SAVED FOR MANUAL INSPECTION ===")
    print(f"New cleaned data saved to: {new_output_path}")
    print(f"Old cleaned data saved to: {old_output_path}")
    
    # Print comparison summary
    print("\n=== COMPARISON RESULTS ===")
    print(f"New dataframe shape: {new_cleaned.shape}, Old dataframe shape: {old_cleaned.shape}")
    
    # Rest of the test code continues as before...
    # Compare columns
    print("\n=== COLUMNS COMPARISON ===")
    new_cols = set(new_cleaned.columns)
    old_cols = set(old_cleaned.columns)
    print(f"Columns in both: {new_cols.intersection(old_cols)}")
    print(f"Columns only in new: {new_cols - old_cols}")
    print(f"Columns only in old: {old_cols - new_cols}")
    
    # Compare numeric columns
    numeric_cols = ['price', 'unit_price', 'units', 'ounces']
    print("\n=== NUMERIC COLUMNS COMPARISON ===")
    
    # Keep track of rows with differences
    diff_indices = set()
    
    for col in numeric_cols:
      if col in new_cleaned.columns and col in old_cleaned.columns:
        new_values = pd.to_numeric(new_cleaned[col], errors='coerce')
        old_values = pd.to_numeric(old_cleaned[col], errors='coerce')
        
        # Calculate differences
        differences = (new_values - old_values).abs()
        max_diff = differences.max()
        
        # Summary statistics
        print(f"\nColumn: {col}")
        print(f"  Max difference: {max_diff}")
        print(f"  Matching values: {(differences < 0.01).sum()} of {len(differences)}")
        
        # Collect indices of rows with differences
        col_diff_indices = differences[differences > 0.01].index
        diff_indices.update(col_diff_indices)
        
        # Show a few examples of differences
        if max_diff > 0.01:
          examples = col_diff_indices[:5]  # Show up to 5 examples
          print(f"  Examples of differences (out of {len(col_diff_indices)} different values):")
          for idx in examples:
            print(f"    Index {idx}: New={new_values[idx]}, Old={old_values[idx]}")
    
    # Print full rows for all differences found
    if diff_indices:
      print("\n=== ROWS WITH DIFFERENCES ===")
      print(f"Found {len(diff_indices)} rows with differences.")
      
      # Sort indices for consistent output
      sorted_indices = sorted(diff_indices)
      for idx in sorted_indices[:20]:  # Limit to first 20 differences to avoid excessive output
        print(f"\nRow index: {idx}")
        print("NEW ROW:")
        print(new_cleaned.loc[idx])
        print("\nOLD ROW:")
        print(old_cleaned.loc[idx])
        print("-" * 50)
      
      if len(sorted_indices) > 20:
        print(f"... and {len(sorted_indices) - 20} more rows with differences")
    
    # Run the assertions as before for test results
    if isinstance(old_cleaned, pd.DataFrame):
      self.assertEqual(new_cleaned.shape, old_cleaned.shape, "DataFrames have different shapes")
      self.assertListEqual(list(new_cleaned.columns), list(old_cleaned.columns), 
          "DataFrames have different columns")
      
      for col in numeric_cols:
        if col in new_cleaned.columns and col in old_cleaned.columns:
          new_values = pd.to_numeric(new_cleaned[col], errors='coerce')
          old_values = pd.to_numeric(old_cleaned[col], errors='coerce')
          
          for new_val, old_val in zip(new_values, old_values):
            if pd.isna(new_val) and pd.isna(old_val):
              continue
            elif pd.isna(new_val) or pd.isna(old_val):
              self.fail(f"NaN mismatch in column {col}")
            else:
              self.assertAlmostEqual(new_val, old_val, places=2,
                msg=f"Values in column {col} don't match")

if __name__ == "__main__":
  unittest.main(buffer=False)
