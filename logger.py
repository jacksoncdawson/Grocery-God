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

import streamlit as st
from datetime import datetime
from db.database import supabase, insert_trip_data, fetch_trip_data, fetch_trip_products


# --- INIT Functions ---

def init_state():
  # Initialize session state for submission
  if "submitted" not in st.session_state:
    st.session_state.submitted = False

  # Initialize session state for products
  if "products" not in st.session_state:
    st.session_state.products = []

  # Initialize session state for page
  if "page" not in st.session_state:
    st.session_state.page = "form"


# --- HELPER Functions --- 

def set_page(page_name):
  st.session_state.page = page_name
  st.rerun()

def handle_trip_submission():
  store = st.session_state.store
  trip_date = st.session_state.trip_date

  # Prepare list of products
  products_to_insert = []
  for i in range(st.session_state.num_products):
    
    # Verify Product Name
    product_name = st.session_state.get(f"product_{i}", "").strip().lower()
    if not product_name:
      st.warning(f"Warning: Product {i+1} is missing a name.")
      return False
    
    # Verify Price
    product_price = st.session_state.get(f"price_{i}", "")
    if not isinstance(product_price, float):
      st.warning(f"Warning: Product {i+1} does not have an appropriate price set.")
      return False
    elif product_price <= 0:
      st.warning(f"Warning: The price set for Product {i+1} is less than or equal to zero.")
      return False

    products_to_insert.append({
      "product": product_name,
      "brand": st.session_state.get(f"brand_{i}", "").strip().lower(),
      "price": st.session_state.get(f"price_{i}", 0.0),
      "sale_price": st.session_state.get(f"sale_price_{i}", "No") == "Yes",
      "units": st.session_state.get(f"units_{i}", 1),
      "ounces": st.session_state.get(f"oz_{i}", None),
    })

  # From db.database
  trip_id = insert_trip_data(store, trip_date, products_to_insert)

  if trip_id:
    st.session_state.trip_id = trip_id  # Store trip ID for further use
    return True
  else:
    st.error("Failed to log trip. Please try again.")
    return False

def load_latest_trip():
  
  latest_trip = fetch_trip_data()
    
  if latest_trip:
    st.session_state.latest_trip = latest_trip
    st.session_state.trip_id = latest_trip["id"]
  else:
    st.session_state.latest_trip = None
    st.session_state.trip_id = None
    st.session_state.trip_products = []
    return
  
  if "trip_products" not in st.session_state:
    st.session_state.trip_products = fetch_trip_products(st.session_state.trip_id)

def reset_trip_data():
  st.session_state.pop("latest_trip", None)
  st.session_state.pop("trip_products", None)
  st.session_state.pop("trip_id", None)
  st.session_state.pop("store", None)
  st.session_state.pop("trip_date", None)
  
  st.session_state.submitted = False
  st.session_state.num_products = 1


# --- Main ---

init_state()

# Form Page
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

    submit_button = st.form_submit_button(label="Submit Trip", use_container_width=True)

    if submit_button:
      if not st.session_state.submitted:
        
        submission_success = handle_trip_submission()
        if submission_success:
          st.session_state.submitted = True
          set_page("summary")
        else:
          st.session_state.submitted = False

# Summary Page
if st.session_state.page == "summary":
  
  load_latest_trip()

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
