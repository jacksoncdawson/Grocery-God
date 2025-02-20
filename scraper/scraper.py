from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import re
from datetime import datetime
from selenium.common.exceptions import TimeoutException

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

    print(f"Valid From: {valid_from}")
    print(f"Valid Until: {valid_until}")

except TimeoutException:
  print("Timeout while trying to get date information.")
  date_text = "Unknown"

finally:
  driver.switch_to.default_content()  # Return to the main content

# Get Product information
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
    
  all_aria_labels = []

  for flyer in flyer_images:
    flyer_items = flyer.find_elements(By.TAG_NAME, "sfml-flyer-image-a")
    
    for item in flyer_items:
      aria_label = item.get_attribute("aria-label")
      if aria_label:
        all_aria_labels.append(aria_label)

    # Define the CSV file path
    csv_file_path = "/Users/jackcdawson/Desktop/dev/Python Projects/Grocery God/scraper/aria_labels.csv"

    # Write data to CSV
    with open(csv_file_path, "w", newline="") as file:
      writer = csv.writer(file)
      writer.writerow([date_text])
      for label in all_aria_labels:
        writer.writerow([label])

  print(f"Scraped {len(all_aria_labels)} product entries and saved to CSV.")

except TimeoutException:
  print("\nEXCEPTION: Timeout while trying to get product information.\n")

finally:
  driver.quit()
