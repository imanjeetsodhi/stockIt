import os
import time
import pandas as pd
import yfinance as yf

NIFTY_50 = [
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "APOLLOHOSP.NS",
    "ASIANPAINT.NS",
    "AXISBANK.NS",
    "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS",
    "BAJAJFINSV.NS",
    "BEL.NS",
    "BHARTIARTL.NS",
    "CIPLA.NS",
    "COALINDIA.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "ETERNAL.NS",
    "GRASIM.NS",
    "HCLTECH.NS",
    "HDFCBANK.NS",
    "HDFCLIFE.NS",
    "HEROMOTOCO.NS",
    "HINDALCO.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "INDUSINDBK.NS",
    "INFY.NS",
    "ITC.NS",
    "JIOFIN.NS",
    "JSWSTEEL.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "M&M.NS",
    "MARUTI.NS",
    "MAXHEALTH.NS",
    "NESTLEIND.NS",
    "NTPC.NS",
    "ONGC.NS",
    "POWERGRID.NS",
    "RELIANCE.NS",
    "SBILIFE.NS",
    "SBIN.NS",
    "SHRIRAMFIN.NS",
    "SUNPHARMA.NS",
    "TATACONSUM.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "TCS.NS",
    "TECHM.NS",
    "TITAN.NS",
    "TRENT.NS",
    "ULTRACEMCO.NS",
    "WIPRO.NS",
]



OUTPUT_DIR = "data/raw"

START_DATE = "2023-01-01"
END_DATE = "2026-09-19"



os.makedirs(OUTPUT_DIR, exist_ok=True)




print("\n==============================================")
print("       NIFTY 50 DATA DOWNLOADER")
print("==============================================\n")

print(f"Stocks to download : {len(NIFTY_50)}")
print(f"Start date         : {START_DATE}")
print(f"End date           : {END_DATE}")
print(f"Output directory   : {OUTPUT_DIR}\n")


successful = []
failed = []


for number, ticker in enumerate(NIFTY_50, start=1):

    print(f"[{number}/{len(NIFTY_50)}] Downloading {ticker}...")

    try:

        data = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            auto_adjust=False,
            progress=False
        )

        if data.empty:
            print(f"   ❌ No data found for {ticker}\n")
            failed.append(ticker)
            continue

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        required_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume"
        ]

        data = data[required_columns].copy()

        data.reset_index(inplace=True)

        data["Stock"] = ticker.replace(".NS", "")

        data = data[
            [
                "Stock",
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Adj Close",
                "Volume"
            ]
        ]

        filename = ticker.replace(".NS", "") + ".csv"

        filepath = os.path.join(
            OUTPUT_DIR,
            filename
        )

        data.to_csv(filepath, index=False)

        print(
            f"   ✅ Saved {len(data)} rows → {filepath}\n"
        )

        successful.append(ticker)

        time.sleep(0.5)

    except Exception as error:

        print(f"ERROR: {error}\n")

        failed.append(ticker)


print(" DOWNLOAD COMPLETE")

print(f"Successful : {len(successful)}")
print(f"Failed     : {len(failed)}")

if failed:

    print("\nFailed stocks:")
    for ticker in failed:
        print(f" - {ticker}")

else:

    print("\nAll Nifty 50 stocks downloaded successfully.")

print(f"\nFiles saved in: {OUTPUT_DIR}/")