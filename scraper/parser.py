import re

def parse_row(row, keyword):
  product, rest = row.split(keyword, 1)
  deal, price = rest.split(",", 1)
  
  if "," in price:
    return None, None, None
  
  product = product.strip()
  deal = f"{keyword.replace(",", "").strip()} {deal.strip()}"
  price = price.strip()
  
  return product, deal, price

def sort_data(raw_data):
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

