"""
Program Name: safeway
Description: This script scrapes price and deal data from safeway weekly ad.
Author: Jack Dawson
Date: 8/24/2025
"""

from grocery_god.scraping.scraper import scrape_safeway, scrape_to_csv

def main():

    # Scrape Safeway
    all_products, valid_from, valid_until = scrape_safeway()

    if not all_products:
        raise ValueError("Scraping completed but no products were found.")

    if not valid_from or not valid_until:
        raise ValueError("Scraping completed but date range is missing.")

    scrape_to_csv(all_products, valid_from, valid_until)


if __name__ == "__main__":
    main()
