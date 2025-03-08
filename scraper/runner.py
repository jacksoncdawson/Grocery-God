import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import glob
import pandas as pd

from scraper import save_safeway_scrape
from cleaner import clean_data
from parser import sort_data
from db.database import upload_scrape, upload_clean_data

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

def main():
  
  save_safeway_scrape()
  
  file_list = glob.glob("scraper/weeklyad_*.csv")
  if not file_list:
    print("❌ Something went wrong... 'save_safeway_scrape()' didn't produce the right file, in the right place.\n")
    return
  
  file_path = file_list[0]
  
  # get date info
  with open(file_path, 'r') as file:
    first_line = file.readline().strip()
    valid_from, valid_until = first_line.split(" - ")
  
  df = setup_df(file_path)
  
  cleaned_df = clean_data(df)
  
  # Upload all data to Supabase
  try:
    
    upload_scrape(file_path)
    
    if isinstance(cleaned_df, pd.DataFrame):
      flyer_id = upload_clean_data(cleaned_df, valid_from, valid_until)
      if flyer_id:
        print(f"✅ Flyer data for the week of {valid_from} is saved in Supabase.\n")
        
  except Exception as e:
    print(f"Something went wrong uploading data to Supabase: {e}\n")

  finally:
    # Clean up
    os.remove(file_path)
    print(f"Deleted the local file: {file_path}\n")


if __name__ == "__main__":
  
  main()
