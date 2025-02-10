"""
Program Name: Logger 
Description: Collects and stores grocery product prices input by the user, with support for multiple products in a single submission
Author: Jack Dawson
Date: 2/1/2025
Version: 1.1
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def set_page(page_name):
  st.session_state.page = page_name
  st.rerun()


# Initialize session state for products
if "products" not in st.session_state:
    st.session_state.products = []

# Initialize session state for page
if "page" not in st.session_state:
    st.session_state.page = "home"


if st.session_state.page == "home":

  st.title("Price Logger")

  st.session_state.store = st.radio(
    "Select a store:", ["Trader Joe's", "Safeway", "Costco"], horizontal=True
  )

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
      
      # Amount
      col1, col2 = st.columns(2)
      with col1:
        st.number_input(f"Units", min_value=1, step=1, key=f"units_{i}")
      with col2:
        st.number_input(
          f"Ounces (if applicable)", min_value=0.0, step=0.01, key=f"oz_{i}"
        )
      st.markdown("---")

    # Submit button
    submit_button = st.form_submit_button(label="Submit")

    if submit_button:
      
      products_to_insert = []

      for i in range(num_products):
        
        brand = st.session_state.get(f"brand_{i}", None).strip()
        product = st.session_state.get(f"product_{i}", None).strip()
        price = st.session_state.get(f"price_{i}", None)
        sale_price = st.session_state.get(f"sale_price{i}", "No") == "Yes"
        units = st.session_state.get(f"units_{i}", None)
        oz = st.session_state.get(f"oz_{i}", None)
      
        if not product:
          st.error(f"Error: Product {i+1} is missing a name.")
          st.stop()
          
        # Store product in session state (for display)
        st.session_state.products.append(
          {
            "brand": brand,
            "product": product,
            "price": price,
            "sale_price": sale_price,
            "units": units,
            "ounces": oz
          }
        )
        
        # Prepare data for Supabase insertion
        products_to_insert.append({
          "store": st.session_state.store,
          "brand": brand,
          "product": product,
          "price": price,
          "sale_price": sale_price,
          "units": units,
          "ounces": oz
        })
        
        # Insert into Supabase
        response = supabase.table("grocery_data").insert(products_to_insert).execute()
      
        if response.get("status_code") == 201:
          st.success("Data successfully saved to Supabase!")
          set_page("form")
        else:
          st.error(f"Failed to save data: {response}")
          st.stop() 

elif st.session_state.page == "form":
  st.title("Trip Logged")

  if st.session_state.products:
    st.write(f"### Submitted {st.session_state.store} Trip: ")
    for product in st.session_state.products:
      
      st.markdown(f"**Product:** {product['product']}")
      
      if product['brand']:
        st.markdown(f"**Brand:** {product['brand']}")
      
      st.markdown(f"**Price:** ${product['price']:.2f}")
      st.markdown(f"**Units:** {product['units']}")
      
      if product['ounces']:
        st.markdown(f"**Ounces:** {product['ounces']}")
      
      st.markdown("---")
