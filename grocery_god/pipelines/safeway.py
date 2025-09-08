"""
Defines the Safeway grocery data pipeline for the Grocery God project.

It provides a function to run the Safeway scraping pipeline, which:
- Scrapes product data and sale date ranges from Safeway using the scraping utilities.
- Validates the presence of product data and date ranges.
- Exports the scraped data to a CSV file.

Functions:
    run_safeway_pipeline(output_path: str | None = None): Runs the Safeway scraping pipeline and exports results.

Usage:
    Run this module as a script to execute the pipeline and save results.
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
