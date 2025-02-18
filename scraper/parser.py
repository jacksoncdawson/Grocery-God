import pandas as pd
import re

def extract_price(text):
    """Extracts the price from the text, handling various formats."""
    price_pattern = r"(\d+\sfor\s\$\d+\.\d+|\$\d+\.\d+\s?(ea)?\s?Member Price?|Starting at\s\$\d+\.\d+|\d+\s/\s\$\d+\swhen you buy \d+|when you buy \d+)"
    match = re.search(price_pattern, text)
    return match.group(0) if match else None

def extract_deal(text):
    """Extracts Safeway-specific deals such as EARN 4X POINTS or discount offers."""
    deal_pattern = r"(EARN \d+X POINTS|\$\d+ OFF Member Price)"
    match = re.search(deal_pattern, text)
    return match.group(0) if match else None

def clean_data(file_path):
    """Reads a CSV file, cleans the deals data, and returns a structured DataFrame."""
    df = pd.read_csv(file_path, header=None, names=["Raw Data"])

    products, deals, prices = [], [], []

    for row in df["Raw Data"]:
        # Extract price
        price = extract_price(row)
        # Extract deal
        deal = extract_deal(row)

        # Remove the extracted price and deal from the string
        clean_row = row
        if price:
            clean_row = clean_row.replace(price, "").strip(", ")
        if deal:
            clean_row = clean_row.replace(deal, "").strip(", ")

        # Remaining text is the product name
        product_name = clean_row.strip(", ")

        products.append(product_name)
        deals.append(deal)
        prices.append(price)

    # Construct cleaned DataFrame
    cleaned_df = pd.DataFrame({
        "Product": products,
        "Safeway Deal": deals,
        "Price": prices
    })

    return cleaned_df

if __name__ == "__main__":
    file_path = "scraper/aria_labels.csv"
    cleaned_df = clean_data(file_path)

    # Save to a cleaned CSV
    cleaned_df.to_csv("cleaned_safeway_deals.csv", index=False)
    print("Cleaned data saved to cleaned_safeway_deals.csv")
