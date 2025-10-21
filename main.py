from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
from datetime import datetime
import schedule
import time as t
#from correlation_analysis import correlation_analysis

def get_driver(headless=True):
    options = Options()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def scrape_coin(driver):
    driver.get("https://coinmarketcap.com/")
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//tbody/tr"))
    )
    rows = driver.find_elements(By.XPATH, "//tbody/tr")[:10]
    data = []
    for row in rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 8:
                continue

            name = cells[2].text.split('\n')[0]
            price = cells[3].text.replace('$', '').replace(',', '')
            change = cells[4].text.replace('%', '').replace(',', '')
            market_cap = cells[7].text.replace('$', '').replace(',', '')

            if not price or not change or not market_cap:
                continue

            data.append([name, float(price), float(change), float(market_cap)])
        except Exception as e:
            print("Skipping row:", e)
            continue
    if not data:
        raise ValueError("No data was scraped — check CoinMarketCap structure.")
    return pd.DataFrame(data, columns=["Coin", "Price", "Change_24h", "MarketCap"])
def save_to_csv(df, filename="data/crypto_data_log.csv"):
    os.makedirs("data", exist_ok=True)
    df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        old_df = pd.read_csv(filename)
        combined = pd.concat([old_df, df], ignore_index=True)
    except FileNotFoundError:
        combined = df
    combined.to_csv(filename, index=False)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Data appended to {filename}")
def job():
    print("\nStarting scheduled scrape...")
    driver = get_driver(headless=True)
    try:
        df = scrape_coin(driver)
        print(df)
        save_to_csv(df)
    except Exception as e:
        print("Error during scrape:", e)
    finally:
        driver.quit()
    print("Scrape cycle complete.")
if __name__ == "__main__":
    driver = get_driver(headless=False)
    df = scrape_coin(driver)
    print(df)
    job()
    schedule.every(30).minutes.do(job)
    #schedule.every().day.at("23:00").do(correlation_analysis)
    print("Scheduler running... Press Ctrl+C to stop.\n")
    while True:
        schedule.run_pending()
        t.sleep(10)
    driver.quit()
