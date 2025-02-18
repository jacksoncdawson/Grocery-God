from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize WebDriver (Ensure chromedriver is installed)
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode (optional)
driver = webdriver.Chrome(options=options)

# Open the Safeway Weekly Ad page
driver.get("https://www.safeway.com/weeklyad/")  # Ensure this is the correct URL

try:
  
    time.sleep(30)
    # Wait for iframes to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

    # Locate and switch to the "Main Panel" iframe
    iframe = driver.find_element(By.XPATH, "//iframe[@title='Main Panel']")
    driver.switch_to.frame(iframe)

    # Wait for the target elements to load inside the iframe
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "sfml-flyer-image")))

    # Find all sfml-flyer-image elements (each represents a section of the flyer)
    flyer_images = driver.find_elements(By.CSS_SELECTOR, 
        "flipp-router flipp-publication-page div div.sfml-wrapper flipp-sfml-component sfml-storefront div sfml-linear-layout sfml-flyer-image"
    )

    all_aria_labels = []  # Store all aria-labels

    # Loop through each flyer section and extract its flyer-image-a elements
    for index, flyer in enumerate(flyer_images, start=1):
        flyer_items = flyer.find_elements(By.TAG_NAME, "sfml-flyer-image-a")
        
        for item in flyer_items:
            aria_label = item.get_attribute("aria-label")
            if aria_label:  # Ensure we capture only non-empty aria-labels
                all_aria_labels.append(aria_label)

    # Print all extracted aria-labels
    print("Extracted aria-labels:")
    for i, label in enumerate(all_aria_labels, start=1):
        print(f"{i}: {label}")

finally:
    # Close the WebDriver
    driver.quit()
