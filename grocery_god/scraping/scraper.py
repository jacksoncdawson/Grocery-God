import csv
import os
import re
import logging
import time
from datetime import datetime
from typing import Tuple, List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def _make_driver() -> webdriver.Chrome:
    """Create a headless Chrome driver suitable for Docker/Cloud."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def _parse_dates(date_text: str) -> Tuple[Optional[str], Optional[str]]:
    date_text = date_text.strip()
    pattern = r"([a-zA-Z]+ \d+[a-zA-Z]+) - ([a-zA-Z]+ \d+[a-zA-Z]+)"

    match = re.search(pattern, date_text)

    if match:
        current_year = datetime.now().year
        valid_from_str = f"{match.group(1)} {current_year}"
        valid_until_str = f"{match.group(2)} {current_year}"

        valid_from = datetime.strptime(valid_from_str, "%b %dth %Y").strftime(
            "%Y-%m-%d"
        )
        valid_until = datetime.strptime(valid_until_str, "%b %dth %Y").strftime(
            "%Y-%m-%d"
        )
        return valid_from, valid_until

    return None, None


def scrape_safeway(retries: int = 3) -> Tuple[List[str], Optional[str], Optional[str]]:
    """
    Scrape the Safeway Weekly Ad.
    Returns: (all_products, valid_from, valid_until)
    """
    attempt = 0
    backoff = 5

    while attempt < retries:
        driver = None
        try:
            driver = _make_driver()
            driver.get("https://www.safeway.com/weeklyad/")
            time.sleep(3)

            # ---- Dates (Navigation Bar iframe) ----
            try:
                nav_iframe = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//iframe[@title='Navigation Bar']")
                    )
                )
                driver.switch_to.frame(nav_iframe)

                css = "span.flipp-filmstrip-pub-dates flipp-validity-dates flipp-translation"
                date_label = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css))
                )
                
                valid_from, valid_until = _parse_dates(date_label.text)
                
                driver.switch_to.default_content()
                
            except TimeoutException:
                logging.error("Timeout extracting date info (attempt %s)", attempt + 1)
                attempt += 1
                time.sleep(backoff)
                continue

            # ---- Products (Main Panel iframe) ----
            all_products = []
            
            try:
                main_iframe = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//iframe[@title='Main Panel']")
                    )
                )
                driver.switch_to.frame(main_iframe)

                WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.TAG_NAME, "sfml-flyer-image"))
                )
                for flyer in driver.find_elements(By.TAG_NAME, "sfml-flyer-image"):
                    for item in flyer.find_elements(By.TAG_NAME, "sfml-flyer-image-a"):
                        label = item.get_attribute("aria-label")
                        if label:
                            all_products.append(label)

            except TimeoutException as e:
                logging.error(
                    "Timeout getting product info (attempt %s): %s", attempt + 1, e
                )
                attempt += 1
                time.sleep(backoff)
                continue

            return all_products, valid_from, valid_until

        except Exception as e:
            logging.exception("Scraper attempt %s failed: %s", attempt + 1, e)
            attempt += 1
            time.sleep(backoff)

        finally:
            try:
                if driver is not None:
                    driver.quit()
            except Exception:
                pass

    # All retries failed
    return [], None, None


def scrape_to_csv(all_products: List[str], valid_from: str, valid_until: str) -> str:
    """Write CSV locally and return the path."""
    
    os.makedirs("./data", exist_ok=True)
    filename = f"./data/weeklyad_{valid_from}.csv"
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([f"{valid_from} - {valid_until}"])
        
        for product in all_products:
            w.writerow([product])
            
    return filename
