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

def setup_df(file_path):
  
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

def delete_csv(file_path):
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
    try:
      delete_csv(file_path)
    except:
      pass


if __name__ == "__main__":
  
  main()
