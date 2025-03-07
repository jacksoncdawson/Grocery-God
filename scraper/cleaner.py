import pandas as pd
import numpy as np
import glob
import re
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.database import upload_clean_data
from parser import sort_data


def clean_price_column(df):
  
  # "" -> None prices
  df["price"] = df["price"].apply(lambda x: None if x == "" else x)
  
  # Remove unwanted words/symbols
  remove_list = ["member price", "$", ",", "or more", "starting at", "ea", "ea."]
  for item in remove_list:
      df["price"] = df["price"].str.replace(item, "", regex=False).str.strip()
  
  df.loc[df["price"].str.contains("lb", na=False), "ounces"] = 16
  df["price"] = df["price"].str.replace("lb", "", regex=False).str.strip()
  
  df["price"], df["unit_price"], df["units"] = zip(*df.apply(extract_price_constraints, axis=1))
  
  return df

def extract_price_constraints(row):
  
  price = row["price"]
  units = 1
  unit_price = None

  if price is None:
    return price, unit_price, units  

  match = re.search(r"when\s*you\s*buy\s*(\d+)", price)
  if match:
    units = int(match.group(1))
    price = price.replace(match.group(0), "").strip()

  match = re.search(r"(\d+)\s*(for|/)\s*(\d+\.\d+|\d+)", price)
  if match:
    total_price = float(match.group(3))
    count = float(match.group(1))
    unit_price = round(total_price / count, 2)
    price = total_price
  else:
    try:
      unit_price = float(price)
      price = unit_price * units
    except ValueError:
      return None, None, 1

  return price, unit_price, units


def clean_deal_column(df):
  
  # Remove unwanted phrases
  remove_list = ["member price", "equal or lesser value"]
  for item in remove_list:
    df["deal"] = df["deal"].str.replace(item, "", regex=False).str.strip()
      
  df["deal"], df["units"], df["unit_price"] = zip(*df.apply(extract_deal_constraints, axis=1))
  
  return df
  
def extract_deal_constraints(row):
    
  deal, units, price, unit_price = row["deal"], row["units"], row["price"], row["unit_price"]
  if not deal:
    return deal, units, unit_price

  # get units
  match = re.search(r"when\s*you\s*buy\s*(\d+)", deal)
  if match:
    units = int(match.group(1))
    deal = deal.replace(match.group(0), "").strip()
    
  # get unit_price
  match = re.search(r"buy\s*(\d+)\s*get\s*(\d+)\s*free", deal)
  if match and price:
    cost = int(match.group(1)) * float(price)
    unit_price = round(cost / units, 2) 
  
  return deal, units, unit_price


def clean_data(file_path):
  
  raw_df = pd.read_csv(file_path, names=["Raw Data"])
  products, deals, prices = sort_data(raw_df["Raw Data"])
  
  # Construct DataFrame
  df = pd.DataFrame({
    "product": products,
    "deal": deals,
    "price": prices,
  })
  
  # Drop rows with both 'deal' and 'price' as NaN
  df = df.dropna(subset=["deal", "price"], how="all")
  
  # Initialize columns
  df["units"] = 1
  df["unit_price"] = None
  df["ounces"] = None

  # Apply cleaning functions
  try:
    df = clean_price_column(df)
    df = clean_deal_column(df)
  except Exception as e:
    raise ValueError(f"Error cleaning data: {e}")

  return df


def run_clean_data():
  file_list = glob.glob("scraper/weeklyad_*.csv")
  
  if file_list:
    file_path = file_list[0]
    
    # get date info
    with open(file_path, 'r') as file:
      first_line = file.readline().strip()
      valid_from, valid_until = first_line.split(" - ")
    
    cleaned_df = clean_data(file_path)
    
    print(cleaned_df)
    
    # if isinstance(cleaned_df, pd.DataFrame):
    #   flyer_id = upload_clean_data(cleaned_df, valid_from, valid_until)
    #   if flyer_id:
    #     print(f"Success! Flyer data for the week of {valid_from} is saved.\n")
    
    # Clean up
    # os.remove(file_path)
    # print(f"Deleted the file: {file_path}\n")
  
  else:
    print("❌ Something went wrong... scraper.py didn't produce the right file, in the right place")

  
if __name__ == "__main__":

  pass
