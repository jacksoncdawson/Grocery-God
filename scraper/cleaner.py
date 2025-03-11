import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import re


def clean_price_column(df: pd.DataFrame) -> pd.DataFrame:

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

def extract_price_constraints(row: pd.Series) -> tuple[float, float, int]:
  
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


def clean_deal_column(df: pd.DataFrame) -> pd.DataFrame:

  # Remove unwanted phrases
  remove_list = ["member price", "equal or lesser value"]
  for item in remove_list:
    df["deal"] = df["deal"].str.replace(item, "", regex=False).str.strip()
      
  df["deal"], df["units"], df["unit_price"] = zip(*df.apply(extract_deal_constraints, axis=1))

  return df
  
def extract_deal_constraints(row: pd.Series) -> tuple[str, int, float]:
    
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


def clean_data(df: pd.DataFrame) -> pd.DataFrame:

  # Drop rows with both 'deal' and 'price' as NaN
  df = df.dropna(subset=["deal", "price"], how="all")

  # Initialize columns
  df["units"] = 1
  df["unit_price"] = None
  df["ounces"] = None

  # Apply cleaning functions
  try:
    df = clean_price_column(df)
  except Exception as e:
    raise Exception(f"Error in clean_price_column: {e}")

  try:
    df = clean_deal_column(df)
  except Exception as e:
    raise Exception(f"Error in clean_deal_column: {e}")

  # Prepare for JSON formatting
  df.replace({pd.NA: None, np.nan: None}, inplace=True)

  return df
