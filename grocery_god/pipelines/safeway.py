"""
Program Name: safeway
Description: This script scrapes price and deal data from safeway weekly ad.
Author: Jack Dawson
Date: 8/24/2025
"""

from grocery_god.scraping.safeway import scrape_safeway, scrape_to_csv


def run_safeway_pipeline(output_path: str | None = None):

    all_products, valid_from, valid_until = scrape_safeway()

    if not valid_from or not valid_until:
        raise ValueError("Scraping completed but date range is missing.")
    if not all_products:
        raise ValueError("Scraping completed but no products were found.")

    return scrape_to_csv(all_products, valid_from, valid_until, output_path=output_path)


if __name__ == "__main__":
    run_safeway_pipeline()
