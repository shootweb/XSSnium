import sys
import os
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_file_extension(target_url):
    parsed_url = urlparse(target_url)
    _, file_extension = os.path.splitext(parsed_url.path)
    logging.debug(f"Extracted file extension: {file_extension}")
    return file_extension.lower()

def fetch_page_content(driver, url):
    try:
        logging.debug(f"Fetching URL: {url}")
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        return driver.page_source
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def read_file_lines(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.read().splitlines()
        logging.debug(f"Read {len(lines)} lines from {file_path}")
        return lines
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        sys.exit(1)

def save_progress(processed, save_file):
    try:
        with open(save_file, 'a') as file:
            file.writelines(f"{item}\n" for item in processed)
        logging.debug(f"Saved {len(processed)} processed combinations to {save_file}")
    except Exception as e:
        logging.error(f"Error saving progress to {save_file}: {e}")

def process_combination(driver, target_url, modifier, data_line, processed_combinations):
    combination = f"{target_url}{modifier}{data_line}"
    if combination in processed_combinations:
        return None  # Already processed
    
    try:
        get_url = f"{target_url}{modifier}{data_line}"
        fetch_page_content(driver, get_url)
        logging.info(f"GET request sent to {get_url}")
        time.sleep(random.uniform(0.15, 0.17))
        return combination
    except Exception as e:
        logging.error(f"Error performing action on {target_url}: {e}")
        return None

if len(sys.argv) != 3:
    logging.error("Usage: python script.py <target_urls_file_path> <payload_file_path>")
    sys.exit(1)

target_urls_file = sys.argv[1]
data_file = sys.argv[2]

target_urls = read_file_lines(target_urls_file)
data_lines = read_file_lines(data_file)

save_file = 'save_point.txt'
processed_combinations = set()

if os.path.exists(save_file):
    try:
        with open(save_file, 'r') as file:
            processed_combinations = set(file.read().splitlines())
        logging.debug(f"Loaded {len(processed_combinations)} processed combinations from save file")
    except Exception as e:
        logging.error(f"Error loading save file {save_file}: {e}")

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--allow-insecure-localhost")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--no-sandbox")

try:
    driver = webdriver.Chrome(options=chrome_options)
except Exception as e:
    logging.error(f"Error initializing WebDriver: {e}")
    sys.exit(1)

try:
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        batch_save = []

        for target_url in target_urls:
            for modifier in ['', '">']:
                for data_line in data_lines:
                    future = executor.submit(process_combination, driver, target_url, modifier, data_line, processed_combinations)
                    futures.append(future)

        for future in as_completed(futures):
            result = future.result()
            if result:
                batch_save.append(result)
                processed_combinations.add(result)

            # Batch save to avoid frequent file I/O
            if len(batch_save) >= 50:
                save_progress(batch_save, save_file)
                batch_save.clear()

        # Final save for any remaining data
        if batch_save:
            save_progress(batch_save, save_file)
except KeyboardInterrupt:
    logging.info("Interrupted by user. Saving progress...")
    save_progress(processed_combinations, save_file)
except Exception as e:
    logging.error(f"Unexpected error: {e}")
finally:
    driver.quit()
    logging.info("Driver closed.")
