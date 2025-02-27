import pandas as pd
import numpy as np
import re
import glob
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.database import upload_clean_data

def sort_data(raw_data):
  products, deals, prices = [], [], []
  
  # Initial Sorting (sort every relevant item by product, deal, price)
  for row in raw_data:
      
    row = row.lower()
    
    # Check if ", , " is contained in the string -> no Safeway Deal
    if ", , " in row:
      product, price = row.split(", , ")
      products.append(product.strip())
      deals.append(None)
      prices.append(price.strip())
        
    # delete "save $x" rows - too much fuss
    elif "save " in row:
      pass
      
    # Check for various Safeway Deals
    elif ", buy " in row:
      product, rest = row.split(", buy", 1)
      deal, price = rest.split(",", 1)
      products.append(product.strip())
      deals.append("buy " + deal.strip())
      prices.append(price.strip()) 
      
    elif ", free " in row:
      product, rest = row.split(", free", 1)
      deal, price = rest.split(",", 1)
      products.append(product.strip())
      deals.append("free " + deal.strip())
      prices.append(price.strip())
      
    elif ", earn " in row:
      product, rest = row.split(", earn", 1)
      deal, price = rest.split(",", 1)
      products.append(product.strip())
      deals.append("earn " + deal.strip())
      prices.append(price.strip())
  
    elif ", up " in row:
      product, rest = row.split(", up", 1)
      deal, price = rest.split(",", 1)
      products.append(product.strip())
      deals.append("up " + deal.strip())
      prices.append(price.strip())
      
    elif ", get " in row:
      product, rest = row.split(", get", 1)
      deal, price = rest.split(",", 1)
      products.append(product.strip())
      deals.append("get " + deal.strip())
      prices.append(price.strip())
      
    elif re.search(r", \$\d+\.\d+ off ", row) or re.search(r", \$\d+ off ", row):
      product, rest = row.split(", $", 1)
      deal, price = rest.split(", ", 1)
      products.append(product.strip())
      deals.append("$" + deal.strip())
      prices.append(price.strip())
      
    elif re.search(r", \d+\% off", row):
      match = re.search(r", (\d+)% off", row)
      if match:
        percent_off = match.group(1) + "%"
        product, rest = row.split(", ", 1)
        deal, price = rest.split(", ", 1)
        products.append(product.strip())
        deals.append(f"{percent_off} off")
        prices.append(price.strip())
    
    elif ", celebrate with " in row:
      product, rest = row.split(", celebrate with ", 1)
      deal, price = rest.split(", ", 1)
      products.append(product.strip())
      deals.append(deal.strip())
      prices.append(price.strip())
      
    elif ", spend $" in row:
      product, rest = row.split(", spend $", 1)
      deal, price = rest.split(", ", 1)
      products.append(product.strip())
      deals.append("spend $" + deal.strip())
      prices.append(price.strip())
      
    else:
      pass # we don't need these rows
      
  return products, deals, prices

def clean_data(file_path):
  raw_df = pd.read_csv(file_path, names=["Raw Data"])
  products, deals, prices = sort_data(raw_df["Raw Data"])
  
  # Construct DataFrame
  df = pd.DataFrame({
    "product": products,
    "deal": deals,
    "price": prices,
  })
  
  # Drop rows that have both "deal" and "price" as NA
  df = df.dropna(subset=["deal", "price"], how='all')
  
  # Drop rows that have a negative price discount 
  df = df[~df["price"].str.contains("off", na=False)]
  df = df[~df["deal"].str.contains("off", na=False)]
  
  # Initialize empty columns for units, unit_price, and ounces
  df["units"] = 1
  df["unit_price"] = None
  df["ounces"] = None

  def clean_price_column(df):
    
    # "" -> None prices
    df["price"] = df["price"].apply(lambda x: None if x == "" else x)
    
    # clean extra symbols and words
    df["price"] = df["price"].str.replace("member price", "", regex=False).str.strip()
    df["price"] = df["price"].str.replace("$", "", regex=False).str.strip()
    df["price"] = df["price"].str.replace(",", "", regex=False).str.strip()
    df["price"] = df["price"].str.replace("or more", "", regex=False).str.strip()
    df["price"] = df["price"].str.replace("starting at", "", regex=False).str.strip()
    
    # clean units
    df["price"] = df["price"].str.replace("ea", "", regex=False).str.strip()
    
    df.loc[df["price"].str.contains("lb", na=False), "ounces"] = "16"
    df["price"] = df["price"].str.replace("lb", "", regex=False).str.strip()
    
    # catch constraints
    def extract_constraints(row):
      
      price = row["price"]
      units = row["units"]
      unit_price = row["unit_price"]

      if price is None:
        return price, unit_price, units  

      match = re.search(r"when\s*you\s*buy\s*(\d+)", price)
      if match:
        units = match.group(1)
        price = price.replace(match.group(0), "").strip()

      match = re.search(r"(\d+)\s*(for|/)\s*(\d+\.\d+|\d+)", price)
      if match:
        total_price = float(match.group(3))
        count = float(match.group(1))
        unit_price = round(total_price / count, 2)
        price = price.replace(match.group(0), match.group(3)).strip()
      else:
        try:
          unit_price = float(price)
        except ValueError:
          unit_price = None

      return price, unit_price, units

    df["price"], df["unit_price"], df["units"] = zip(*df.apply(extract_constraints, axis=1))
    
    return df

  df = clean_price_column(df)
  
  def clean_deal_column(df):
    # remove "member price"
    df["deal"] = df["deal"].str.replace("member price", "", regex=False).str.strip()

    # remove "equal or lesser value" 
    df["deal"] = df["deal"].str.replace("equal or lesser value", "", regex=False).str.strip()
    
    def extract_units(row):
      
      deal, units, price, unit_price = row["deal"], row["units"], row["price"], row["unit_price"]
      if not deal:
        return deal, units, unit_price

      # get units
      match = re.search(r"when\s*you\s*buy\s*(\d+)", deal)
      if match:
        units = match.group(1)
        deal = deal.replace(match.group(0), "").strip()
        
      # get unit_price
      match = re.search(r"buy\s*(\d+)\s*get\s*(\d+)\s*free", deal)
      if match:
        if price:
          cost = int(match.group(1)) * float(price)
          unit_price = float(cost) / int(units)
        else:
          unit_price = None
      
      return deal, units, unit_price
        
    df["deal"], df["units"], df["unit_price"] = zip(*df.apply(extract_units, axis=1))
  
  clean_deal_column(df)
  
  # Prepare for JSON formatting
  df.replace({pd.NA: None, np.nan: None}, inplace=True)
  
  return df


if __name__ == "__main__":
  
  file_list = glob.glob("scraper/weeklyad_*.csv")
  
  if file_list:
    file_path = file_list[0]
    
    # get date info
    with open(file_path, 'r') as file:
      first_line = file.readline().strip()
      valid_from, valid_until = first_line.split(" - ")
    
    cleaned_df = clean_data(file_path)

    flyer_id = upload_clean_data(cleaned_df, valid_from, valid_until)
    if flyer_id:
      print(f"Success! Flyer data for the week of {valid_from} is saved.")
  
    # # Clean up
    # os.remove(file_path)
    # print(f"Deleted the file: {file_path}")
  
  else:
    print("Something went wrong... scraper.py didn't produce the right file, in the right place")
