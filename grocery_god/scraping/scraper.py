"""
Program Name: Grocery God Safeway Scraper
Description: Scrapes weekly ad data from Safeway's website and saves the data to a CSV file.
Author: Jack Dawson
Date: 3/12/2025

Modules:
- sys: For system-specific parameters and functions.
- os: For interacting with the operating system.
- csv: For reading and writing CSV files.
- re: For regular expression operations.
- logging: For logging error messages.
- time: For adding delays.
- selenium: For web scraping and browser automation.
- datetime: For manipulating dates and times.

Functions:
- scrape_safeway: Scrapes the Safeway weekly ad page, extracts product information and date range, and returns the data.
- save_safeway_scrape: Manages the scraping process and writes the scraped data to a CSV file.

Usage:
1. The script initializes a headless Chrome WebDriver to scrape the Safeway weekly ad page.
2. The scrape_safeway function extracts the date range and product information from the page.
3. The save_safeway_scrape function writes the extracted data to a CSV file.
4. The script can be run directly to perform the scraping and data saving process.
"""

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
                    EC.presence_of_element_located(
                        (By.XPATH, "//iframe[@title='Navigation Bar']")
                    )
                )
                driver.switch_to.frame(navigation_bar)

                # Wait for the date label inside the iframe
                date_label = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "span.flipp-filmstrip-pub-dates flipp-validity-dates flipp-translation",
                        )
                    )
                )

                date_text = date_label.text.strip()

                # Extract the date range from the date_label text
                date_pattern = r"([a-zA-Z]+ \d+[a-zA-Z]+) - ([a-zA-Z]+ \d+[a-zA-Z]+)"
                match = re.search(date_pattern, date_text)

                if match:
                    current_year = datetime.now().year
                    valid_from_str = f"{match.group(1)} {current_year}"
                    valid_until_str = f"{match.group(2)} {current_year}"

                    valid_from = datetime.strptime(
                        valid_from_str, "%b %dth %Y"
                    ).strftime("%Y-%m-%d")
                    valid_until = datetime.strptime(
                        valid_until_str, "%b %dth %Y"
                    ).strftime("%Y-%m-%d")

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
                    EC.presence_of_element_located(
                        (By.XPATH, "//iframe[@title='Main Panel']")
                    )
                )
                driver.switch_to.frame(main_panel)

                # Wait for at least one product image to appear
                WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.TAG_NAME, "sfml-flyer-image"))
                )

                # Find all flyer images
                flyer_images = driver.find_elements(By.TAG_NAME, "sfml-flyer-image")

                for flyer in flyer_images:

                    flyer_items = flyer.find_elements(By.TAG_NAME, "sfml-flyer-image-a")
                    for item in flyer_items:
                        product_info = item.get_attribute("aria-label")
                        if product_info:
                            all_products.append(product_info)

            except TimeoutException as e:
                logging.error(
                    f"Scraper timed out getting product information (attempt {attempt + 1}): {e}"
                )
                attempt += 1
                continue

            return all_products, valid_from, valid_until

        except Exception as e:
            logging.error(f"Scraper attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(5)  # Wait before retrying

        finally:
            driver.quit()


def scrape_to_csv(all_products: list[str], valid_from: str, valid_until: str) -> None:
    filename = f"./data/weeklyad_{valid_from}.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([f"{valid_from} - {valid_until}"])

        for product in all_products:
            writer.writerow([product])

    return filename

if __name__ == "__main__":

    pass
