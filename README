# Grocery God 
## Last Updated: 2/27/2025

## Overview
Grocery God is a comprehensive tool designed to streamline grocery shopping by collecting and analyzing data from various stores. The project features a web app for logging grocery purchases, a scraper for collecting weekly deals from Safeway, and a data cleaning process to ensure the data is ready for analysis. All data is stored in a PostgreSQL database using Supabase.

## Current Features
- **Web App**: Collects grocery shopping data at various stores.
- **Scraper**: Uses Selenium to scrape weekly deals from Safeway.
- **Data Cleaning**: Utilizes Pandas to clean and organize the scraped data.
- **Database Storage**: Stores all data in a PostgreSQL database using Supabase.

## Future Plans
- **Data Insights**: Use the collected data to provide insights on where the best prices are, saving time on planning grocery runs. This will be achieved using PostgreSQL and Tableau.
- **Additional Scrapers**: Collect weekly deals from other grocers.
- **Automation**: Automate the scrape, clean, and upload process locally using cron jobs (or remotely via github actions).

## Project Structure

### Modules and Functions

#### `scraper/scraper.py`
- **scrape_safeway**: Scrapes Safeway's weekly ad page for product information and date range.
- **write_safeway_scrape**: Writes the scraped data to a CSV file and uploads it to Supabase.

#### `scraper/parser.py`
- **sort_data**: Sorts raw data into products, deals, and prices.
- **clean_data**: Cleans and organizes the raw data into a structured format.
- **run_clean_data**: Runs the data cleaning process and uploads the cleaned data to Supabase.

#### `scraper/runner.py`
- **main**: Runs the scraping and data cleaning processes sequentially.

#### `logger.py`
- **init_state**: Initializes the session state for the web app.
- **set_page**: Sets the current page in the Streamlit session state.
- **handle_trip_submission**: Handles the submission of trip data and validates the input.
- **load_latest_trip**: Loads the latest trip data from the database.
- **reset_trip_data**: Resets the trip-related data in the session state.

#### `db/database.py`
- **fetch_trip_data**: Fetches the latest grocery trip data from the database.
- **fetch_trip_products**: Fetches products for a given trip.
- **insert_trip_data**: Inserts trip and product data into the database.
- **upload_scrape**: Uploads a scrape file to Supabase Storage.
- **upload_clean_data**: Uploads cleaned data to the database.

## Additional Files
- **`.env`**: Contains environment variables for the project.
- **`.gitignore`**: Specifies files and directories to be ignored by Git.
- **`requirements.txt`**: Lists the dependencies required for the project.
- **`TODO`**: Contains a list of tasks and future improvements for the project.


