import csv

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from news_extract import scrape_fox_data

SHOW_MORE_BUTTON_SELECTOR = 'div.button.load-more.js-load-more'  # Update this selector as needed


def click_load_more_button(driver):
    """Clicks the 'Show More' button on the page."""
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, SHOW_MORE_BUTTON_SELECTOR))
        ).click()
        return True
    except Exception as e:
        print(f"Failed to click load more: {e}")
        return False


def scrape_section(driver, section_url, base_url, max_articles=100):
    """Scrapes a specific section of Fox News for article URLs."""
    driver.get(section_url)
    temp_urls = set()

    while len(temp_urls) < max_articles:
        current_len = len(temp_urls)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith("/"):
                href = base_url + href
            if href.startswith(section_url) and "video" not in href:
                temp_urls.add(href)

        if len(temp_urls) == current_len and not click_load_more_button(driver):
            print(f"No more 'Show More' button to click or no new articles found in {section_url}.")
            break

        time.sleep(2)  # Wait for new content to load

    return temp_urls


base_url = "https://www.foxnews.com"
sections = [
    f"{base_url}/sports",
    f"{base_url}/politics",
    f"{base_url}/entertainment",
    f"{base_url}/tech",
    f"{base_url}/us",
]

# Initialize WebDriver
cService = ChromeService(executable_path="D:\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=cService)

articles_data = []

for section in sections:
    urls = scrape_section(driver, section, base_url, 500)  # Set max_articles as needed
    print(f"Number of links collected from {section}: {len(urls)}")
    for url in urls:
        print(url)
    category = section.split('/')[-1].replace('_', ' ').title()
    articles_data.extend(scrape_fox_data(driver, urls, category.title()))  # Pass category to scrape function

driver.quit()

# Write the scraped data to a CSV file
with open('fox_news_articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['published_date', 'headline', 'publisher', 'article_content', 'category']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(articles_data)