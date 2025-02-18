import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# Fetch the latest trip from the database.
def fetch_trip_data():
  response = supabase.table("trips").select("*").order("id", desc=True).limit(1).execute()
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
  
  trip_id = trip_response.data[0]["id"]

  # Update products with trip_id
  for product in products:
    product["trip_id"] = trip_id
  
  supabase.table("trip_products").insert(products).execute()
  
  return trip_id
