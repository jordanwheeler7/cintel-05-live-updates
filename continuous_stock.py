"""
Purpose: Illustrate addition of continuous information. 

This is a simple example that uses a deque to store the last 15 minutes of
temperature readings for three locations.

The data is updated every minute.

Continuous information might also come from a database, a data lake, a data warehouse, or a cloud service.

----------------------------
Live Stock Price Data
-----------------------------

We use the yfinance package to get live stock price data.

-----------------------
Keeping Secrets Secret
-----------------------

Keep secrets in a .env file - load it, read the values.
Add the .env file to your .gitignore so you don't publish it to GitHub.
We usually include a .env-example file to illustrate the format.

"""


# Standard Library
import asyncio
from datetime import datetime
from pathlib import Path
import os
from random import randint
import yfinance as yf

# External Packages
import pandas as pd
from collections import deque
from dotenv import load_dotenv

# Local Imports
from fetch import fetch_from_url
from util_logger import setup_logger

# Set up a file logger
logger, log_filename = setup_logger(__file__)


def lookup_ticker(company):
    company_dictionary = {
        "Cadence Design Systems": "CDNS",
        "Synopys": "SNPS",
        "Tractor Supply Company": "TSCO",
        "Lululemon Ahtletica Inc.": "LULU",
        "Arch Capital Group Ltd.": "ACGL",
        "Costco Wholesale Corporation": "COST",
        "Brown & Brown Inc.": "BRO",
        "Thermo Fisher Scientific Inc.": "TMO",
        "CDW Corporation": "CDW",
        "Intuit Inc.": "INTU",
    }
    

async def get_stock_price(ticker):
    logger.info("Calling get_stock_price for {ticker}")
    # stock = yf.Ticker(ticker) # uncomment when ready to use real data #This gets stock data for the ticker
    # price = stock.history(period="1d").tail(1)["Close"][0] #This gets the closing price for the stock
    price = randint(132, 148)  # This is a random number generator for testing
    return price

# Function to create or overwrite the CSV file with column headings
def init_csv_file(file_path):
    df_empty = pd.DataFrame(
        columns=["Location", "Latitude", "Longitude", "Time", "Temp_F"]
    )
    df_empty.to_csv(file_path, index=False)    
    
async def update_csv_ticker():
    """Update the CSV file with the latest location information."""
    logger.info("Calling update_csv_stock_price")
    try:
        companies = ["Cadence Design Systems", "Synopys", "Tractor Supply Company", "Lululemon Ahtletica Inc.", "Arch Capital Group Ltd.", "Costco Wholesale Corporation", "Brown & Brown Inc.", "Thermo Fisher Scientific Inc.", "CDW Corporation", "Intuit Inc."]
        update_interval = 60  # Update every 1 minute (60 seconds)
        total_runtime = 15 * 60  # Total runtime maximum of 15 minutes
        num_updates = 10  # Keep the most recent 10 readings
        logger.info(f"update_interval: {update_interval}")
        logger.info(f"total_runtime: {total_runtime}")
        logger.info(f"num_updates: {num_updates}")

        # Use a deque to store just the last, most recent 10 readings in order
        records_deque = deque(maxlen=num_updates)

        fp = Path(__file__).parent.joinpath("data").joinpath("mtcars_location.csv")

        # Check if the file exists, if not, create it with only the column headings
        if not os.path.exists(fp):
            init_csv_file(fp)

        logger.info(f"Initialized csv file at {fp}")

        for _ in range(num_updates):  # To get num_updates readings
            for location in locations:
                lat, long = lookup_lat_long(location)
                new_temp = await get_temperature_from_openweathermap(lat, long)
                time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time
                new_record = {
                    "Location": location,
                    "Latitude": lat,
                    "Longitude": long,
                    "Time": time_now,
                    "Temp_F": new_temp,
                }
                records_deque.append(new_record)

            # Use the deque to make a DataFrame
            df = pd.DataFrame(records_deque)

            # Save the DataFrame to the CSV file, deleting its contents before writing
            df.to_csv(fp, index=False, mode="w")
            logger.info(f"Saving temperatures to {fp}")

            # Wait for update_interval seconds before the next reading
            await asyncio.sleep(update_interval)

    except Exception as e:
        logger.error(f"ERROR in update_csv_location: {e}")
