import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Set up Selenium WebDriver in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL of the main page
base_url = "https://22f3001919.github.io/tds_project_1_may_24/"
driver.get(base_url)
time.sleep(2)  # Wait for the page to load

# Extract all links on the main page
links = [a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, "a")]

# Storage for extracted data
all_data = []

# Visit each link and extract JSON data
for link in links:
    driver.get(link)
    time.sleep(2)  # Allow time for JavaScript to load

    # Get the page source and search for JSON data
    page_source = driver.page_source
    start_index = page_source.find("const data =") + len("const data =")
    end_index = page_source.find(";", start_index)
    
    if start_index > 10 and end_index > 0:
        json_text = page_source[start_index:end_index].strip()
        try:
            data = json.loads(json_text)
            all_data.extend(data)  # Append extracted data
        except json.JSONDecodeError:
            print(f"Could not parse JSON from {link}")

# Close the browser
driver.quit()

# Save data to DataFrame and Excel
if all_data:
    df = pd.DataFrame(all_data)
    df.to_excel("scraped_data.xlsx", index=False)
    print("Data successfully saved to scraped_data.xlsx!")
else:
    print("No data extracted. Check JavaScript loading issues.")