import os
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd

load_dotenv(override=True)

# Initialize Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

""" Logger DB Functions """

# Fetch the latest trip from the database.
def fetch_trip_data():
  response = supabase.table("trips").select("*").order("trip_id", desc=True).limit(1).execute()
  return response.data[0] if response.data else None

# Fetch products for a given trip.
def fetch_trip_products(trip_id):
  response = supabase.table("trip_products").select("*").eq("trip_id", trip_id).execute()
  return response.data if response.data else []

# Insert trip and product data
def insert_trip_data(store, trip_date, products):
  trip_data = {"store": store, "trip_date": trip_date}
  trip_response = supabase.table("trips").insert(trip_data).execute()
  
  if not trip_response.data or len(trip_response.data) == 0:
    return None
  
  trip_id = trip_response.data[0]["trip_id"]

  # Update products with trip_id
  for product in products:
    product["trip_id"] = trip_id
  
  supabase.table("trip_products").insert(products).execute()
  
  return trip_id


""" Scraper DB Functions """

# Upload a scrape to Supabase Storage
def upload_scrape(file_path, bucket_name="scrapes", folder_name="safeway_flyers"):

  # Confirm file exists
  if not os.path.exists(file_path):
    print(f"ERROR: File {file_path} does not exist!")
    return False

  with open(file_path, "rb") as file:
    file_content = file.read()

  destination_path = f"{folder_name}/{os.path.basename(file_path)}"

  try:
    response = supabase.storage.from_(bucket_name).upload(
      destination_path,
      file_content,
      {"content-type": "text/csv"}  
    )

    if response:
      print(f"✅ File uploaded successfully to {destination_path}\n")
      return True
    elif isinstance(response, dict) and "error" in response:
      print(f"ERROR: {response['error']}\n")
      return False
    else:
      print("❌ Unknown Error: Upload failed without details.\n")
      return False

  except Exception as e:
    print(f"🔥 Exception occurred during upload: {e}\n")
    return False

def upload_clean_data(clean_data, valid_from, valid_until):
  
  # Insert into flyers table
  flyer_data = {
    "store": "safeway",
    "valid_from": valid_from,
    "valid_until": valid_until
  }
  flyer_response = supabase.table("flyers").insert(flyer_data).execute()
  
  if not flyer_response.data or len(flyer_response.data) == 0:
    return None
  
  flyer_id = flyer_response.data[0]["flyer_id"]
  
  # Prepare products data
  products_data = clean_data.to_dict(orient="records")
  for product in products_data:
    product["flyer_id"] = flyer_id
  
  # Insert into products table
  supabase.table("flyer_products").insert(products_data).execute()
  
  return flyer_id