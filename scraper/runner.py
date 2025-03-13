"""
Program Name: Grocery God Scraper Runner
Description: This script cleans and processes price and deal data from a grocery dataset.
Author: Jack Dawson
Date: 3/12/2025

Modules:
- sys: Provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter.
- os: Provides a way of using operating system dependent functionality like reading or writing to the file system.
- glob: Finds all the pathnames matching a specified pattern according to the rules used by the Unix shell.
- pandas as pd: A powerful data analysis and manipulation library for Python.
- logging: Provides a flexible framework for emitting log messages from Python programs.

Functions:
- setup_df(file_path: str) -> pd.DataFrame: Reads a CSV file, sorts the data, and constructs a DataFrame.
- delete_csv(file_path: str) -> None: Deletes a specified CSV file from the local file system.
- main() -> None: The main function that orchestrates the scraping, cleaning, and uploading of grocery data.

Usage:
- Run the script directly to execute the main function, which will scrape data, process it, and upload it to a database.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import glob
import pandas as pd
import logging

from scraper import save_safeway_scrape
from cleaner import clean_data
from parser import sort_data
from db.database import upload_scrape, upload_clean_data

logging.basicConfig(filename="runner_errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def setup_df(file_path: str) -> pd.DataFrame:
  
  # Read Flyer
  raw_df = pd.read_csv(file_path, names=["Raw Data"])
  
  # Sort Flyer
  products, deals, prices = sort_data(raw_df["Raw Data"])
  
  # Construct DataFrame
  df = pd.DataFrame({
    "product": products,
    "deal": deals,
    "price": prices,
  })
  
  return df

def delete_csv(file_path: str) -> None:
  try:
    os.remove(file_path)
    logging.info(f"Deleted the local file: {file_path}\n")
  except Exception as e:
    logging.warning(f"Failed to delete file {file_path}: {e}")


def main():
  try:
    # Scrape Safeway & Save in CSV file
    try:
      save_safeway_scrape()
    except Exception as e:
      raise RuntimeError(f"Error in save_safeway_scrape: {e}")
    
    # Get file_path
    file_list = glob.glob("scraper/weeklyad_*.csv")
    if not file_list:
      raise Exception("save_safeway_scrape() did not produce a file in the expected location.")
    file_path = file_list[0]
    
    # Get Date info
    try:
      with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        valid_from, valid_until = first_line.split(" - ")
    except Exception as e:
      raise Exception(f"Failed to read file '{file_path}': {e}")
    
    df = setup_df(file_path)
    
    # Clean Data
    try:
      cleaned_df = clean_data(df)
    except Exception as e:
      raise Exception(f"Error in clean_data: {e}")
    
    
    # Upload raw scrape to Supabase
    try:
      upload_scrape(file_path)
    except Exception as e:
      raise Exception(f"Error in upload_scrape: {e}")
    
    # Insert flyer data to Supabase
    try:
      if isinstance(cleaned_df, pd.DataFrame):
        flyer_id = upload_clean_data(cleaned_df, valid_from, valid_until)
        if flyer_id:
          logging.info(f"Flyer data for the week of {valid_from} saved in Supabase.")
    except Exception as e:
      raise Exception(f"Error in upload_clean_data: {e}")
        
  except Exception as e:
    logging.error(f"Failure in runner.py: {e}")
    
  finally:
    delete_csv(file_path)


if __name__ == "__main__":
  
  main()
