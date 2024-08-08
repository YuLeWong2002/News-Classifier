import csv
import re
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


# Function to click the "Load More" button
def click_load_more_button():
    try:
        # Wait for the button to be clickable
        load_more_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="pagination-next-button"]'))
        )
        # Scroll into view if needed
        driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
        # Scroll away the overlay if present
        overlay = driver.find_element(By.CLASS_NAME, "zephr-overlay")
        if overlay.is_displayed():
            driver.execute_script("arguments[0].style.display = 'none';", overlay)
        # Click the button
        load_more_button.click()
        return True
    except Exception as e:
        print("Error clicking button:", e)
        return False


# bbc news functions
def scrape_func(driver, unique_article_links, categories):
    # List to store the scraped data
    scraped_data = []
    # Iterate over the extracted article URLs and scrape relevant information
    for article_url in unique_article_links:
        driver.get(article_url)
        time.sleep(2)

        # Get the page source of the article page
        article_page_source = driver.page_source

        # Parse the article page source
        article_soup = BeautifulSoup(article_page_source, 'html.parser')

        # Extract relevant information
        published_date_element = article_soup.find('time', {'class': 'sc-1c2a0c78-9 ducqaA'})
        published_date = published_date_element.text if published_date_element else None

        headline_element = article_soup.find('h1', {'class': 'sc-82e6a0ec-0 fxXQuy'})
        headline = headline_element.text.strip() if headline_element else None

        publisher = "BBC News"  # You can hardcode this since it's constant for all articles from the same source

        article_content = ''
        content_blocks = article_soup.find_all('section', {'data-component': 'text-block'})
        for block in content_blocks:
            paragraphs = block.find_all('p', {'class': 'sc-e1853509-0 bmLndb'})
            for paragraph in paragraphs:
                article_content += paragraph.text.strip() + '\n'

        # Assuming the category is available on the homepage
        category = categories  # You can customize this based on the actual category of the article
        article_data = {
            'published_date': published_date,
            'headline': headline,
            'publisher': publisher,
            'article_content': article_content,
            'category': category
        }

        # Print or use the extracted information as needed
        print("Published Date:", published_date)
        print("Headline:", headline)
        print("Publisher:", publisher)
        print("Article Content:", article_content)
        print("Category:", category)
        print("----")

        # Append the dictionary to the list
        scraped_data.append(article_data)
    # Return the scraped data
    return scraped_data


def get_articles_url(driver, soup, section_url, unique_article_links, max_urls):
    # Regular expression to match hyphen and replace with underscore
    pattern = r"\."  # Matches a hyphen followed by one or more letters
    escaped_section_url = re.sub(pattern, r"\\.", section_url)
    print(escaped_section_url)
    url_pattern = re.compile(fr"{escaped_section_url}-\d+$")
    url_pattern1 = re.compile(r"https://www\.bbc\.com/news/world-us-canada-\d+$")
    print(url_pattern)
    print(url_pattern1)
    exclude_keywords = ["av", "live", "help"]

    for link in soup.find_all('a', href=True):
        absolute_url = urljoin(section_url, link['href'])

        # Check if the URL matches the pattern and doesn't contain any of the excluded keywords
        if url_pattern.match(absolute_url) and not any(keyword in absolute_url for keyword in exclude_keywords):
            unique_article_links.add(absolute_url)
    print("Number of links created:", len(unique_article_links))

    while click_load_more_button():
        pass


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
                                [us_canada_format, business_format, technology_format, science_environment_format,
                                 entertainment_format]):
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load
    section_source = driver.page_source
    soup = BeautifulSoup(section_source, 'html.parser')
    unique_article_links = set()
    get_articles_url(driver, soup, category_format, unique_article_links, max_articles_per_section)

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
