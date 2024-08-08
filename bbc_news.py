import csv
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from news_extract import scrape_func, get_articles_url


us_canada_url = "https://www.bbc.com/news/world/us_and_canada"
business_url = "https://www.bbc.com/news/business"
technology_url = "https://www.bbc.com/news/technology"
science_url = "https://www.bbc.com/news/science_and_environment"
entertainment_url = "https://www.bbc.com/news/entertainment_and_arts"

cService = webdriver.ChromeService(executable_path="D:\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=cService)

# The common format for this type of news
us_canada_format = "https://www.bbc.com/news/world-us-canada"
business_format = "https://www.bbc.com/news/business"
technology_format = "https://www.bbc.com/news/technology"
science_environment_format = "https://www.bbc.com/news/science-environment"
entertainment_format = "https://www.bbc.com/news/entertainment-arts"

max_articles_per_section = 150

# Initialize lists to hold articles data from different categories
articles_data = []

# Scrape data for each category
for url, category_format in zip([us_canada_url, business_url, technology_url, science_url, entertainment_url],
                                [us_canada_format, business_format, technology_format, science_environment_format, entertainment_format]):
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load
    section_source = driver.page_source
    soup = BeautifulSoup(section_source, 'html.parser')
    unique_article_links = set()
    get_articles_url(driver, soup, category_format, unique_article_links, max_articles_per_section, 1)

    # Scrape articles from the updated set of unique article URLs
    category = category_format.split('/')[-1].replace('_', ' ').title()
    articles_data.extend(scrape_func(driver, unique_article_links, category))

# Quit the driver
driver.quit()

# Write the scraped data to a CSV file
with open('bbc_news_articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['published_date', 'headline', 'publisher', 'article_content', 'category']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(articles_data)
