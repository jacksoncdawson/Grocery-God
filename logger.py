"""
Program Name: Logger 
Description: Collects and stores grocery product prices input by the user
Author: Jack Dawson
Date: 2/1/2025
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_supabase_client():
  SUPABASE_URL = os.getenv("SUPABASE_URL")
  SUPABASE_KEY = os.getenv("SUPABASE_KEY")
  return create_client(SUPABASE_URL, SUPABASE_KEY)

def set_page(page_name):
  st.session_state.page = page_name
  st.rerun()

def fetch_latest_trip():
  if "latest_trip" not in st.session_state:
    response = supabase.table("trips").select("*").order("id", desc=True).limit(1).execute()
    if response.data:
      st.session_state.latest_trip = response.data[0]
      st.session_state.trip_id = response.data[0]["id"]
    else:
      st.session_state.latest_trip = None
      st.session_state.trip_id = None
      
def fetch_trip_products():
  if "trip_products" not in st.session_state and st.session_state.trip_id:
    response = supabase.table("trip_products").select("*").eq("trip_id", st.session_state.trip_id).execute()
    st.session_state.trip_products = response.data if response.data else []

def reset_trip_data():
  for key in ["latest_trip", "trip_products", "trip_id"]:
    st.session_state.pop(key, None)

supabase = get_supabase_client()

# Initialize session state for products
if "products" not in st.session_state:
    st.session_state.products = []

# Initialize session state for page
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":

  st.title("Price Logger")

  col1, col2 = st.columns(2)
  with col1:
    st.session_state.store = st.selectbox(
      "Select a store:", ["Trader Joe's", "Safeway", "Costco"]
    )
  with col2:
    trip_date = st.date_input("Grocery Trip Date", datetime.now()).isoformat()

  # Input for the number of products
  num_products = st.number_input("Number of products:", min_value=1, step=1)

  # Form for entering products
  with st.form(key="grocery_form"):

    for i in range(num_products):
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

    # Submit button
    submit_button = st.form_submit_button(label="Submit", disabled=st.session_state.get("submitting", False))

    if submit_button:
      st.session_state["submitting"] = True
      
      # Insert new trip into 'trips' table
      trip_data = {"store": st.session_state.store, "trip_date":trip_date}
      trip_response = supabase.table("trips").insert(trip_data).execute()
      
      # Retrieve the inserted trip ID
      if trip_response.data and (len(trip_response.data) > 0):
        trip_id = trip_response.data[0]["id"]
      else:
        st.error("Error: Could not log trip.")
        st.stop()
      
      # Prepare list of products to insert
      products_to_insert = []
      for i in range(num_products):
        
        brand = st.session_state.get(f"brand_{i}", None).strip().lower()
        product = st.session_state.get(f"product_{i}", None).strip().lower()
        price = st.session_state.get(f"price_{i}", None)
        sale_price = st.session_state.get(f"sale_price_{i}", "No") == "Yes"
        units = st.session_state.get(f"units_{i}", None)
        ounces = st.session_state.get(f"oz_{i}", None)
      
        if not product:
          st.error(f"Error: Product {i+1} is missing a name.")
          st.stop()
        
        # Prepare data for Supabase insertion
        products_to_insert.append({
          "trip_id": trip_id,
          "product": product,
          "brand": brand,
          "price": price,
          "sale_price": sale_price,
          "units": units,
          "ounces": ounces
        })
        
      # Insert into Supabase
      if products_to_insert:
        products_response = supabase.table("trip_products").insert(products_to_insert).execute()
      
      # Open up Submission
      st.session_state["submitting"] = False
      
      # Finally, go to form page
      set_page("form")


if st.session_state.page == "form":
  
  fetch_latest_trip()
  fetch_trip_products()

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
        set_page("home")
    
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
