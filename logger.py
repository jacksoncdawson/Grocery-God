"""
Program Name: Logger 
Description: Allows users to log purchased grocery products. The data is stored in a Supabase database for future reference and analysis.
Author: Jack Dawson
Date: 2/16/2025

Modules:
- os: For accessing environment variables.
- streamlit: For creating the web interface.
- supabase: For interacting with the Supabase database.
- dotenv: For loading environment variables from a .env file.
- datetime: For handling date and time operations.

Functions:
- get_supabase_client: Initializes and returns a Supabase client using environment variables.
- set_page: Sets the current page in the Streamlit session state and triggers a rerun.
- fetch_trip_data: Fetches the latest trip data and associated products from the Supabase database.
- insert_trip_data: Validates and inserts trip and product data into the Supabase database.
- reset_trip_data: Resets the trip-related data in the Streamlit session state.

Usage:
1. The user selects a store and date for the grocery trip.
2. The user inputs the number of products and details for each product.
3. Upon submission, the data is validated and stored in the Supabase database.
4. The user can view a summary of the logged trip and products.

Note:
- Ensure that the SUPABASE_URL and SUPABASE_KEY environment variables are set in the .env file.
- The program uses Streamlit for the web interface, so it should be run in a Streamlit environment.
"""

import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_supabase_client():
  SUPABASE_URL = os.getenv("SUPABASE_URL")
  SUPABASE_KEY = os.getenv("SUPABASE_KEY")
  return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

def set_page(page_name):
  st.session_state.page = page_name
  st.rerun()

def fetch_trip_data():
  if "latest_trip" not in st.session_state:
    response = supabase.table("trips").select("*").order("id", desc=True).limit(1).execute()
    if response.data:
      st.session_state.latest_trip = response.data[0]
      st.session_state.trip_id = response.data[0]["id"]
    else:
      st.session_state.latest_trip = None
      st.session_state.trip_id = None
      st.session_state.trip_products = []
      return
      
  if "trip_products" not in st.session_state:
    response = supabase.table("trip_products").select("*").eq("trip_id", st.session_state.trip_id).execute()
    st.session_state.trip_products = response.data if response.data else []

def insert_trip_data():
  trip_data = {"store": st.session_state.store, "trip_date": st.session_state.trip_date}
  
  # Validate products 
  products_to_insert = []
  for i in range(st.session_state.num_products):
    
    product = st.session_state.get(f"product_{i}", "").strip().lower()
    if not product:
      st.warning(f"Warning: Product {i+1} is missing a name.")
      return None

    products_to_insert.append({
      "trip_id": None, # Temporary setting
      "product": product,
      "brand": st.session_state.get(f"brand_{i}", "").strip().lower(),
      "price": st.session_state.get(f"price_{i}", 0.0),
      "sale_price": st.session_state.get(f"sale_price_{i}", "No") == "Yes",
      "units": st.session_state.get(f"units_{i}", 1),
      "ounces": st.session_state.get(f"oz_{i}", None)
      })
    
  # Now insert the trip
  trip_response = supabase.table("trips").insert(trip_data).execute()
  if not trip_response.data or len(trip_response.data) == 0:
    return None
  
  trip_id = trip_response.data[0]["id"]

  # Update product entries with trip_id
  for product in products_to_insert:
    product["trip_id"] = trip_id
  
  # Insert products in batch
  batch_response = supabase.table("trip_products").insert(products_to_insert).execute()
  if not batch_response.data or len(trip_response.data) == 0:
    return None
  
  return trip_id

def reset_trip_data():
  st.session_state.pop("latest_trip", None)
  st.session_state.pop("trip_products", None)
  st.session_state.pop("trip_id", None)
  st.session_state.pop("store", None)
  st.session_state.pop("trip_date", None)
  
  st.session_state.submitted = False
  st.session_state.num_products = 1

# Initialize session state for submission
if "submitted" not in st.session_state:
  st.session_state.submitted = False

# Initialize session state for products
if "products" not in st.session_state:
  st.session_state.products = []

# Initialize session state for page
if "page" not in st.session_state:
  st.session_state.page = "form"

if st.session_state.page == "form":

  st.title("Price Logger")

  col1, col2 = st.columns(2)
  with col1:
    st.session_state.store = st.selectbox(
      "Select a store:", ["Trader Joe's", "Safeway", "Costco"]
    )
  with col2:
    st.session_state.trip_date = st.date_input("Grocery Trip Date", datetime.now()).isoformat()

  # Input for the number of products
  num_products = st.number_input("Number of products:", min_value=1, step=1, key="num_products")

  # Form for entering products
  with st.form(key="grocery_form"):

    for i in range(st.session_state.num_products):
      st.markdown(f"### Product {i+1}")
      st.text_input(f"Product", key=f"product_{i}") 
      st.text_input(f"Brand", key=f"brand_{i}")

      # Price
      col1, col2 = st.columns(2)
      with col1:
        st.number_input(f"Price", min_value=0.0, step=0.01, key=f"price_{i}")
      with col2:
        st.radio(f"Sale Price?", ["Yes", "No"], key=f"sale_price_{i}", index=1, horizontal=True)
      
      # Quantity
      col1, col2 = st.columns(2)
      with col1:
        st.number_input(f"Units", min_value=1, step=1, key=f"units_{i}")
      with col2:
        st.number_input(
          f"Ounces (if applicable)", min_value=0.0, step=0.01, key=f"oz_{i}"
        )
      st.markdown("---")

    submit_button = st.form_submit_button(label="Submit")

    if submit_button:
      if not st.session_state.submitted:
        
        st.session_state.submitted = True
        
        trip_id = insert_trip_data()
        if not trip_id:
          st.session_state.submitted = False
          st.stop()

        set_page("summary")

if st.session_state.page == "summary":
  
  fetch_trip_data()

  if not st.session_state.latest_trip:
    st.error("No trips found.")
  else:
    st.title("Trip Logged!")
    
    latest_trip = st.session_state.latest_trip
    trip_id = st.session_state.trip_id
    
    trip_products = st.session_state.trip_products

    # Display trip details
    
    col1, col2 = st.columns(2)
    
    with col1:
      st.markdown(f"### Store: {latest_trip['store']}")
      st.markdown(f"**Date:** {latest_trip['trip_date']}")
    with col2:
      if st.button("**Log New Trip?**"):
        reset_trip_data()
        set_page("form")
    
    st.markdown("---")

    # Display trip items
    if trip_products:
      st.markdown("### Purchased Products:")
      for product in trip_products:
        
        st.markdown(f"**Product:** {product["product"]}")
        
        if product["brand"]:
          st.markdown(f"**Brand:** {product["brand"]}")
          
        st.markdown(f"**Price:** ${product['price']:.2f}")
        st.markdown(f"**Units:** {product['units']}")
        
        if product["ounces"]:
          st.markdown(f"**Ounces:** {product["ounces"]}")
        
        sale_text = "Yes" if product["sale_price"] else "No"
        st.markdown(f"**On Sale?** {sale_text}")
        
        st.markdown("---")
    else:
      st.write("No items found for this trip.")
