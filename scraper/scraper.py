"""
Program Name: Grocery God Safeway Scraper
Description: Scrapes weekly ad data from Safeway's website, extracts product information and date range, and saves the data to a CSV file. The data is then uploaded to a database.
Author: Jack Dawson
Date: 2/27/2025

Modules:
- sys: For system-specific parameters and functions.
- os: For interacting with the operating system.
- csv: For reading and writing CSV files.
- re: For regular expression operations.
- selenium: For web scraping and browser automation.
- datetime: For manipulating dates and times.
- db.database: For uploading scraped data to the database.

Functions:
- scrape_safeway: Scrapes the Safeway weekly ad page, extracts product information and date range, and returns the data.
- write_safeway_scrape: Manages the scraping process, writes the scraped data to a CSV file, and uploads the file to the database.

Usage:
1. The script initializes a headless Chrome WebDriver to scrape the Safeway weekly ad page.
2. The scrape_safeway function extracts the date range and product information from the page.
3. The write_safeway_scrape function writes the extracted data to a CSV file and uploads it to the database.
4. The script can be run directly to perform the scraping and data upload process.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import csv
import re
import logging
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime

logging.basicConfig(filename="scraper_errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def scrape_safeway(retries: int = 3) -> tuple[list[str], str, str]:
  attempt = 0
  while attempt < retries:
    try:
      
      # Initialize WebDriver 
      options = webdriver.ChromeOptions()
      options.add_argument("--headless")  
      options.add_argument("--window-size=1920,1080")
      options.add_argument("--no-sandbox")
      options.add_argument("--disable-dev-shm-usage")
      driver = webdriver.Chrome(options=options)

      # Open the Safeway Weekly Ad page
      driver.get("https://www.safeway.com/weeklyad/")
      time.sleep(3)

      # Get Date Information --->
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
        
        driver.switch_to.default_content()  # Return to the main content

      except TimeoutException as e:
        logging.error(f"Timeout extracting date info (attempt {attempt + 1})")
        attempt += 1
        continue
        

    # Get Product information --->
    
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
            logging.warning(f"Error extracting product info from flyer: {e}")
            continue

      except TimeoutException as e:
        logging.error(f"Scraper timed out getting product information (attempt {attempt + 1}): {e}")
        attempt += 1
        continue

      return all_products, valid_from, valid_until

    except Exception as e:
      logging.error(f"Scraper attempt {attempt + 1} failed: {e}")
      attempt += 1
      time.sleep(5)  # Wait before retrying

    finally:
      try:
        driver.quit()
      except:
        pass # driver already quit

def save_safeway_scrape() -> None:
  
  # Scrape Safeway
  try:
    all_products, valid_from, valid_until = scrape_safeway()
    
    if not all_products:
      raise ValueError("Scraping completed but no products were found.")
      
    if not valid_from or not valid_until:
      raise ValueError("Scraping completed but date range is missing.")

  except TimeoutException as e:
    raise TimeoutException(f"Safeway scraping timed out: {e}")

  except Exception as e:
    raise RuntimeError(f"Error in scrape_safeway: {e}")
  

  # Write scrape to CSV file
  try:
    filename = f"weeklyad_{valid_from}.csv"
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    with open(file_path, "w", newline="") as file:
      writer = csv.writer(file)
      writer.writerow([f"{valid_from} - {valid_until}"])
      
      for product in all_products:
        writer.writerow([product])
      
  except IOError as e:
    raise IOError(f"Error writing to CSV file '{filename}': {e}")
  
  except Exception as e:
    raise RuntimeError(f"Unexpected error in save_safeway_scrape: {e}")
    

if __name__ == "__main__":

  save_safeway_scrape()
