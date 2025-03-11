"""
Program Name: Grocery God Database Handler
Description: Handles database operations for the Grocery God application, including fetching, inserting, and uploading data to Supabase.
Author: Jack Dawson
Date: 2/27/2025

Modules:
- os: For interacting with the operating system and environment variables.
- supabase: For interacting with the Supabase database.
- dotenv: For loading environment variables from a .env file.
- pandas: For data manipulation and analysis.

Functions:
- fetch_trip_data: Fetches the latest trip data from the database.
- fetch_trip_products: Fetches products for a given trip from the database.
- insert_trip_data: Inserts trip and product data into the database.
- upload_scrape: Uploads a scrape file to Supabase Storage.
- upload_clean_data: Uploads cleaned data to the database, including flyer and product information.

Usage:
1. The script initializes a Supabase client using environment variables for the URL and key.
2. The fetch_trip_data function retrieves the most recent trip data from the "trips" table.
3. The fetch_trip_products function retrieves products associated with a specific trip from the "trip_products" table.
4. The insert_trip_data function inserts new trip data and associated products into the database.
5. The upload_scrape function uploads a specified file to a designated bucket and folder in Supabase Storage.
6. The upload_clean_data function inserts cleaned flyer and product data into the "flyers" and "flyer_products" tables, respectively.
"""

import os, sys
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import logging
logging.basicConfig(filename="database_errors.log",level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv(override=True)

# Initialize Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

""" Logger DB Functions """

# Fetch the latest trip from the database.
def fetch_trip_data() -> dict:
  response = supabase.table("trips").select("*").order("trip_id", desc=True).limit(1).execute()
  return response.data[0] if response.data else None

# Fetch products for a given trip.
def fetch_trip_products(trip_id: int) -> list:
  response = supabase.table("trip_products").select("*").eq("trip_id", trip_id).execute()
  return response.data if response.data else []

# Insert trip and product data
def insert_trip_data(store: str, trip_date: str, products: list) -> int:
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

# Upload a raw scrape to Supabase Storage
def upload_scrape(file_path: str, bucket_name: str = "scrapes", folder_name: str = "safeway_flyers") -> None:

  # Confirm file exists
  if not os.path.exists(file_path):
    raise FileNotFoundError(f"File {file_path} does not exist.")

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
      logging.info(f"Raw Scrape uploaded successfully to {destination_path}")
    elif isinstance(response, dict) and "error" in response:
      raise RuntimeError(f"Bad Raw Scrape upload response: {response['error']}")
    else:
      raise RuntimeError("Unknown Error: Upload failed without details.")
  except Exception as e:
    raise RuntimeError(f"Error uploading file to Supabase: {e}")

# Upload cleaned flyer data to the database
def upload_clean_data(clean_data: pd.DataFrame, valid_from: str, valid_until: str) -> None:
  
  # Insert into flyers table
  flyer_data = {
    "store": "safeway",
    "valid_from": valid_from,
    "valid_until": valid_until
  }
  
  flyer_response = supabase.table("flyers").insert(flyer_data).execute()
  if not flyer_response.data or len(flyer_response.data) == 0:
    raise RuntimeError("Failed to insert flyer data into the database.")

  flyer_id = flyer_response.data[0]["flyer_id"]
  
  # Prepare products data
  products_data = clean_data.to_dict(orient="records")
  for product in products_data:
    product["flyer_id"] = flyer_id
  
  # Insert into products table
  try:
    supabase.table("flyer_products").insert(products_data).execute()
  except Exception as e:
    try:
      supabase.table("flyers").delete().eq("flyer_id", flyer_id).execute()
    except:
      pass
    raise RuntimeError(f"Failed to insert flyer products into the database: {e}")