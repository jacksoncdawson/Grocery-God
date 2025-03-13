"""
Program Name: Grocery God Parser
Description: This script cleans and processes price and deal data from a grocery dataset.
Author: Jack Dawson
Date: 3/12/2025

Modules:
- re: Provides regular expression matching operations.
- pandas as pd: A powerful data analysis and manipulation library for Python.

Functions:
- parse_row(row: str, keyword: str) -> list[str, str, float]: Parses a row of data to extract product, deal, and price information based on a keyword.
- sort_data(raw_data: pd.Series) -> tuple[list[str], list[str], list[str]]: Sorts raw data into lists of products, deals, and prices, filtering out unwanted rows.

Usage:
- Import the script and call the `sort_data` function with a pandas Series containing raw grocery data.
"""

import re
import pandas as pd

def parse_row(row: str, keyword: str) -> list[str, str, float]:
  product, rest = row.split(keyword, 1)
  deal, price = rest.split(",", 1)
  
  if "," in price:
    return None, None, None
  
  product = product.strip()
  deal = f"{keyword.replace(",", "").strip()} {deal.strip()}"
  price = price.strip()
  
  return product, deal, price

def sort_data(raw_data: pd.Series) -> tuple[list[str], list[str], list[str]]:
  products, deals, prices = [], [], []
  
  keywords = [", buy ", ", free ", ", earn ", ", up ", ", get ", ", celebrate with ", ", spend $"]
  
  for row in raw_data:
    row = row.lower()
  
    # Discard discount rows
    if "save " in row:
      continue
    
    if re.search(r", \$\d+\.\d+ off ", row) or re.search(r", \$\d+ off ", row):
      continue
      
    if re.search(r", \d+\% off", row):
      continue
  
    # Rows we want
    if ", , " in row:
      product, price = row.split(", , ")
      if "," in price:
        continue
    
      products.append(product.strip())
      deals.append(None)
      prices.append(price.strip())
    
    else:
      for kw in keywords:
        if kw in row:
          product, deal, price = parse_row(row, kw)
          
          if product or deal or price: 
            products.append(product)
            deals.append(deal)
            prices.append(price)
          
  return products, deals, prices

