import csv
import os
from datetime import datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Define the folder to store the CSV files
OUTPUT_FOLDER = "consent_results"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def sanitize_filename(url):
    """
    Generates a safe file name based on the URL and includes the current date.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace(".", "_")
    current_date = datetime.now().strftime("%Y-%m-%d")
    return f"{OUTPUT_FOLDER}/{domain}_{current_date}.csv"

def parse_html_and_find_cookies(html, output_file):
    """
    Analyzes the HTML and extracts elements related to cookies and consent management.
    Saves the filtered results into a CSV file.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Keywords for both older CybotCookiebot and newer CKY implementations
    keywords = ["cookie", "consent", "gdpr", "privacy", "opt-in", "opt-out", "cky", "Cybot"]

    detected_elements = []
    for tag in ["div", "iframe", "script", "link"]:
        elements = soup.find_all(tag, attrs=True)
        for el in elements:
            # Look for keywords in attributes or inner text
            if any(keyword in str(el.attrs).lower() or keyword in el.get_text().lower() for keyword in keywords):
                detected_elements.append({
                    "Tag": tag,
                    "Attributes": str(el.attrs),
                    "Text": el.get_text(strip=True),
                    "OuterHTML": str(el)
                })

    if detected_elements:
        print(f"[DEBUG] Detected {len(detected_elements)} elements related to cookies.")
    else:
        print("[DEBUG] No elements detected related to cookies.")

    # Save results to a CSV file
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Tag", "Attributes", "Text", "OuterHTML"])
        writer.writeheader()
        writer.writerows(detected_elements)

    print(f"[INFO] Saved {len(detected_elements)} consent-related elements to {output_file}")

def wait_for_page_load(driver, timeout=15):
    """
    Waits for the page to load by checking the presence of <html>.
    """
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
        time.sleep(3)  # Additional time for dynamic elements to load
    except Exception as e:
        print(f"[ERROR] Page did not load properly: {e}")

def check_iframes_for_consent(driver, output_file):
    """
    Checks iframes for elements related to cookies and consent management.
    """
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"[DEBUG] Found {len(iframes)} iframes on the page.")
    for index, iframe in enumerate(iframes):
        try:
            print(f"[INFO] Checking iframe {index + 1}/{len(iframes)}: {iframe.get_attribute('src')}")
            driver.switch_to.frame(iframe)

            # Analyze consent-related elements in the iframe
            iframe_html = driver.page_source
            parse_html_and_find_cookies(iframe_html, output_file)

            driver.switch_to.default_content()  # Switch back to the main DOM
        except Exception as e:
            print(f"[ERROR] Problem with iframe: {e}")
            driver.switch_to.default_content()

def check_consent_mode_for_url(url):
    """
    Opens the page, retrieves the HTML, and analyzes it for Consent Mode elements.
    """
    output_file = sanitize_filename(url)

    # Setup headless Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"[INFO] Opening page: {url}")
        driver.get(url)
        wait_for_page_load(driver)

        # Check iframes for consent-related elements
        check_iframes_for_consent(driver, output_file)

        # Get the current HTML of the page
        html = driver.page_source

        # Analyze the HTML and save results to CSV
        parse_html_and_find_cookies(html, output_file)

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

    finally:
        driver.quit()

def main():
    """
    Main function to input URL and trigger the analysis.
    """
    while True:
        url = input("Enter the URL of the page to analyze (or type 'exit' to quit): ").strip()
        if url.lower() == "exit":
            print("[INFO] Exiting the application.")
            break

        check_consent_mode_for_url(url)

if __name__ == "__main__":
    main()
