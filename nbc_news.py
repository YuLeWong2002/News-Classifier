import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from news_extract import scrape_nbc_data

cService = webdriver.ChromeService(executable_path="D:\\chromedriver\\chromedriver.exe")
driver = webdriver.Chrome(service=cService)


# Function to navigate to a section and collect unique URLs
def collect_unique_urls_from_section(section_url):
    driver.get(section_url)

    # Wait for the page to load and collect URLs until "Load More" is unavailable
    while click_load_more_button():
        pass

    # Parse the current page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_links = soup.find_all('a', href=True)

    # Add unique URLs to the set
    temp_urls = set()
    for link in all_links:
        href = link['href']
        if section_url in href and "video" not in href and "live-blog" not in href:
            temp_urls.add(href)

    print(f"Number of links after adding from {section_url}: {len(temp_urls)}")
    return temp_urls


# Function to click the "Load More" button
def click_load_more_button():
    try:
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="button-hover-animation"]'))
        )
        load_more_button.click()
        return True
    except:
        return False


# Define sections to collect URLs from
sections = [
    "https://www.nbcnews.com/news/us-news",
    "https://www.nbcnews.com/politics",
    "https://www.nbcnews.com/business",
    "https://www.nbcnews.com/health"
]

# Initialize list to hold articles data from different categories
articles_data = []

# Iterate over sections and collect URLs
for section in sections:
    unique_urls = collect_unique_urls_from_section(section)  # Collect unique URLs from each section
    category = section.split('/')[-1].replace('_', ' ').title()
    articles_data.extend(scrape_nbc_data(driver, unique_urls, category.title()))  # Pass category to scrape function

# Print some article data for verification
for article in articles_data[:5]:  # Print first 5 articles for brevity
    print(article['headline'])
    print(article['category'])
    print("----")

# Close the browser
driver.quit()

# Write the scraped data to a CSV file
with open('nbc_news_articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['published_date', 'headline', 'publisher', 'article_content', 'category']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(articles_data)