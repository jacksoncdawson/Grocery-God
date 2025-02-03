"""
Program Name: Logger 
Description: Collects and stores grocery product prices input by the user, with support for multiple products in a single submission
Author: Jack Dawson
Date: 2/1/2025
Version: 1.1
"""

import os
import streamlit as st
import csv


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
      st.number_input(f"Price", min_value=0.0, step=0.01, key=f"price_{i}")
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

      for i in range(num_products):
        
        brand = st.session_state.get(f"brand_{i}", None).strip()
        product = st.session_state.get(f"product_{i}", None).strip()
        price = st.session_state.get(f"price_{i}", None)
        units = st.session_state.get(f"units_{i}", None)
        oz = st.session_state.get(f"oz_{i}", None)
        if oz == 0.00:
          oz = None
      
        if product:
          st.session_state.products.append(
            {
              "brand": brand,
              "product": product,
              "price": price,
              "units": units,
              "ounces": oz
            }
          )
          
        # Define the CSV file path
        csv_file_path = os.path.join(os.path.dirname(__file__), "grocery_log.csv")

        # Check if the CSV file exists
        file_exists = os.path.isfile(csv_file_path)

        # Open the CSV file in append mode
        with open(csv_file_path, mode="a", newline="") as file:
          writer = csv.writer(file)
          
          # Write the header if the file does not exist
          if not file_exists:
            writer.writerow(["Store", "Brand", "Product", "Price", "Units", "Ounces"])
          
          # Write the product data
          writer.writerow([
            st.session_state.store,
            brand,
            product,
            price,
            units,
            oz
          ])

      set_page("form")
      

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
