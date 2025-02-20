import pandas as pd
import re

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
      
    elif ", save " in row:
      product, rest = row.split(", save", 1)
      deal, price = rest.split(",", 1)
      products.append(product.strip())
      deals.append("save " + deal.strip())
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
  
  # Initialize empty columns for unit and restraints
  df["unit"] = None
  df["restraints"] = None
  
  for index, row in df.iterrows():

    # clean extra symbols and words
    if "member price" in row["price"]:
      df.at[index, "price"] = row["price"].replace("member price", "").strip()
      row["price"] = df.at[index, "price"]
      
    if "$" in row["price"]:
      df.at[index, "price"] = row["price"].replace("$", "").strip()
      row["price"] = df.at[index, "price"]
      
    # clean & collect units
    if "ea" in row["price"]:
      df.at[index, "price"] = row["price"].replace("ea", "").strip()
      row["price"] = df.at[index, "price"]
      
      df.at[index, "unit"] = 

    if "lb" in row["price"]:
      df.at[index, "price"] = row["price"].replace("ea", "").strip()
      row["price"] = df.at[index, "price"]
    
    # # Extract unit information
    # if " lb" in row["price"]:
    #   df.at[index, "unit"] = "lb"
    #   df.at[index, "price"] = row["price"].replace(" lb", "").strip()
    # elif " ea" in row["price"]:
    #   df.at[index, "unit"] = "ea"
    #   df.at[index, "price"] = row["price"].replace(" ea", "").strip()
    
    print(index, df.at[index, "price"])
    
    
  
  return df

if __name__ == "__main__":
  file_path = "scraper/aria_labels.csv"
  cleaned_df = clean_data(file_path)

  # Save to a cleaned CSV
  cleaned_df.to_csv("/Users/jackcdawson/Desktop/dev/Python Projects/Grocery God/scraper/cleaned_safeway_deals.csv", index=False)
  print("Cleaned data saved to cleaned_safeway_deals.csv")
