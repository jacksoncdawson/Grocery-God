"""
Program Name: safeway
Description: This script cleans and processes price and deal data from safeway weekly ad.
Author: Jack Dawson
Date: 8/24/2025

Modules:
- pandas as pd: A powerful data analysis and manipulation library for Python.
- logging: Provides a flexible framework for emitting log messages from Python programs.

Functions:
- setup_df(file_path: str) -> pd.DataFrame: Reads a CSV file, sorts the data, and constructs a DataFrame.
- delete_csv(file_path: str) -> None: Deletes a specified CSV file from the local file system.
- main() -> None: The main function that orchestrates the scraping, cleaning, and uploading of grocery data.

Usage:
- Run the script directly to execute the main function, which will scrape data, process it, and upload it to a database.
"""

import pandas as pd
import logging

from grocery_god.scraping.scraper import scrape_safeway, scrape_to_csv
from grocery_god.cleaning.cleaner import clean_data
from grocery_god.parsing.parser import sort_data
from grocery_god.db.database import upload_scrape, upload_clean_data
from selenium.common.exceptions import TimeoutException

logging.basicConfig(
    filename="scraper_errors.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def setup_df(file_path: str) -> pd.DataFrame:

    # Read Flyer
    raw_df = pd.read_csv(file_path, names=["Raw Data"])

    # Sort Flyer
    products, deals, prices = sort_data(raw_df["Raw Data"])

    # Construct DataFrame
    df = pd.DataFrame(
        {
            "product": products,
            "deal": deals,
            "price": prices,
        }
    )

    return df


def main():

    # Scrape Safeway
    all_products, valid_from, valid_until = scrape_safeway()

    if not all_products:
        raise ValueError("Scraping completed but no products were found.")

    if not valid_from or not valid_until:
        raise ValueError("Scraping completed but date range is missing.")

    # Save scrape to CSV
    filename = scrape_to_csv(all_products, valid_from, valid_until)

    df = setup_df(filename)

    cleaned_df = clean_data(df)

    # upload_scrape(file_path)

    # # Insert flyer data to Supabase
    # if isinstance(cleaned_df, pd.DataFrame):
    #     flyer_id = upload_clean_data(cleaned_df, valid_from, valid_until)
    #     if flyer_id:
    #         logging.info(
    #             f"Flyer data for the week of {valid_from} saved in Supabase."
    #         )

    logging.info(
        f"Success: Scraped {len(cleaned_df["product"])} of {len(all_products)} total entries."
    )


if __name__ == "__main__":
    main()
