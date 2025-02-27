import sys
import os
import csv
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import upload_scrape

def scrape_safeway():

  # Initialize WebDriver 
  options = webdriver.ChromeOptions()
  options.add_argument("--headless")  
  options.add_argument("--disable-gpu")
  options.add_argument("--window-size=1920,1080")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  driver = webdriver.Chrome(options=options)

  # Open the Safeway Weekly Ad page
  driver.get("https://www.safeway.com/weeklyad/")


  # Get Date Information
  valid_from = None
  valid_until = None

  try:
    # Wait for the "Navigation Bar" iframe to be available and switch to it
    navigation_bar = WebDriverWait(driver, 30).until(
      EC.presence_of_element_located((By.XPATH, "//iframe[@title='Navigation Bar']"))
    )
    driver.switch_to.frame(navigation_bar)

    # Wait for the date label inside the iframe
    date_label = WebDriverWait(driver, 30).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, "span.flipp-filmstrip-pub-dates flipp-validity-dates flipp-translation"))
    )

    date_text = date_label.text.strip()

    # Extract the date range from the date_label text
    date_pattern = r"([a-zA-Z]+ \d+[a-zA-Z]+) - ([a-zA-Z]+ \d+[a-zA-Z]+)"
    match = re.search(date_pattern, date_text)

    if match:
      current_year = datetime.now().year
      valid_from_str = f"{match.group(1)} {current_year}"
      valid_until_str = f"{match.group(2)} {current_year}"

      valid_from = datetime.strptime(valid_from_str, "%b %dth %Y").strftime("%Y-%m-%d")
      valid_until = datetime.strptime(valid_until_str, "%b %dth %Y").strftime("%Y-%m-%d")

  except TimeoutException:
    print("Timeout while trying to get date information.")
    date_text = "Unknown"

  finally:
    driver.switch_to.default_content()  # Return to the main content


  # Get Product information
  all_products = []

  try:
    # Wait for the "Main Panel" iframe and switch to it
    main_panel = WebDriverWait(driver, 30).until(
      EC.presence_of_element_located((By.XPATH, "//iframe[@title='Main Panel']"))
    )
    driver.switch_to.frame(main_panel)

    # Wait for at least one product image to appear
    WebDriverWait(driver, 30).until(
      EC.visibility_of_element_located((By.TAG_NAME, "sfml-flyer-image"))
    )

    # Find all flyer images
    flyer_images = driver.find_elements(By.TAG_NAME, "sfml-flyer-image")

    for flyer in flyer_images:
      try:
        flyer_items = flyer.find_elements(By.TAG_NAME, "sfml-flyer-image-a")
        
        for item in flyer_items:
          product_info = item.get_attribute("aria-label")
          if product_info:
            all_products.append(product_info)
      except Exception as e:
        print(f"Error extracting product info: {e}")

  except TimeoutException:
    print("\nEXCEPTION: Timeout while trying to get product information.\n")

  finally:
    driver.quit()

  return all_products, valid_from, valid_until

def write_safeway_scrape():
  
  print("\nScraping safeway.com ...\n")
  all_products, valid_from, valid_until = scrape_safeway()
  
  if valid_from and valid_until and all_products:

    # Generate file name based on date
    filename = f"weeklyad_{valid_from}.csv"

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    # Write data to CSV
    with open(file_path, "w", newline="") as file:
      writer = csv.writer(file)
      writer.writerow([f"{valid_from} - {valid_until}"])
      for product in all_products:
        writer.writerow([product])

    print(f"Scraped {len(all_products)} product entries and saved to {filename}.\n")

    # TODO: this needs to be a separate module
    upload_scrape(file_path)
  

if __name__ == "__main__":
  
  write_safeway_scrape()