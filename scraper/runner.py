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

from scraper import scrape_safeway, scrape_to_csv
from cleaner import clean_data
from parser import sort_data
from db.database import upload_scrape, upload_clean_data
from selenium.common.exceptions import TimeoutException

logging.basicConfig(filename="scraper_errors.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

def main():
  try:
    
    # Scrape Safeway
    all_products, valid_from, valid_until = scrape_safeway()
      
    if not all_products:
      raise ValueError("Scraping completed but no products were found.")
      
    if not valid_from or not valid_until:
      raise ValueError("Scraping completed but date range is missing.")

    # Save scrape to CSV
    scrape_to_csv(all_products, valid_from, valid_until)
    
    
    # Get file_path
    file_list = glob.glob("scraper/weeklyad_*.csv")
    if not file_list:
      raise Exception("scrape_to_csv() did not produce a file in the expected location.")
    file_path = file_list[0]
    
    
    # Get Dates
    with open(file_path, 'r') as file:
      first_line = file.readline().strip()
      valid_from, valid_until = first_line.split(" - ")

    
    df = setup_df(file_path)
    
    cleaned_df = clean_data(df)
    
    
    # Upload raw scrape to Supabase
    upload_scrape(file_path)
    
    # Insert flyer data to Supabase
    if isinstance(cleaned_df, pd.DataFrame):
      flyer_id = upload_clean_data(cleaned_df, valid_from, valid_until)
      if flyer_id:
        logging.info(f"Flyer data for the week of {valid_from} saved in Supabase.")
    
    # Report Status
    logging.info(f"Success: Scraped {len(cleaned_df["product"])} of {len(all_products)} total entries.")
        
  except Exception as e:
    logging.error(f"Failure in runner.py: {e}")
    
  finally:
    os.remove(file_path)


if __name__ == "__main__":
  
  main()
