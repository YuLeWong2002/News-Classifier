from urllib.parse import urljoin
from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import re
import logging


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
        published_date_element = article_soup.find('time', {'data-testid': 'timestamp'})
        published_date = published_date_element['datetime'] if published_date_element else None

        headline_element = article_soup.find('h1', {'id': 'main-heading'})
        headline = headline_element.text.strip() if headline_element else None

        publisher = "BBC News"  # You can hardcode this since it's constant for all articles from the same source

        article_content = ''
        content_blocks = article_soup.find_all('div', {'data-component': 'text-block'})
        for block in content_blocks:
            paragraphs = block.find_all('p')
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


def get_articles_url(driver, soup, section_url, unique_article_links, max_urls, current_page_number):
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

    next_page_number = current_page_number + 1

    try:
        next_page_link_xpath = f"//a[contains(@href, '?page={next_page_number}')]"
        next_page_link = driver.find_element(By.XPATH, next_page_link_xpath)
        if next_page_link and len(unique_article_links) < max_urls:
            next_page_link.click()
            WebDriverWait(driver, 10).until(EC.url_changes(section_url))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            get_articles_url(driver, soup, section_url, unique_article_links, max_urls,
                             current_page_number=next_page_number)
    except Exception as e:
        logging.error(f"Error: {e}")


# nbc news function
#  to click the "Load More" button
def click_load_more_button(driver):
    try:
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="button-hover-animation"]'))
        )
        load_more_button.click()
        return True
    except:
        return False


# Function to click a section button by its CSS selector
def click_section_button(driver, css_selector):
    try:
        section_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        section_button.click()
        return True
    except:
        return False


def scrape_nbc_data(driver, unique_article_links, categories):
    # List to store the scraped data
    scraped_data = []
    # Iterate over the extracted article URLs and scrape relevant information
    for article_url in unique_article_links:
        # Skip non-news URLs
        if 'facebook.com' in article_url or 'twitter.com' in article_url:
            continue

        try:
            driver.get(article_url)
            time.sleep(2)  # Adding a small delay after page load

            # Get the page source of the article page
            article_page_source = driver.page_source

            # Parse the article page source
            article_soup = BeautifulSoup(article_page_source, 'html.parser')

            # Extract relevant information
            published_date_element = article_soup.find('time', {'data-testid': 'timestamp__datePublished'})
            published_date = published_date_element['datetime'] if published_date_element else None

            headline_element = article_soup.find('h1', {'class': 'article-hero-headline__htag'})
            headline = headline_element.text.strip() if headline_element else None

            publisher = "NBC News"  # You can hardcode this since it's constant for all articles from the same source

            article_content = ''
            content_blocks = article_soup.find_all('div', {'class': 'article-body__content'})
            for block in content_blocks:
                paragraphs = block.find_all('p')
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

        except TimeoutException:
            print(f"Timeout while loading article: {article_url}. Skipping...")
            continue  # Skip to the next article in case of TimeoutException

    # Return the scraped data
    return scraped_data


def scrape_fox_data(driver, unique_article_links, categories):
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
        published_date_element = article_soup.find('span', class_='article-date')
        published_date = None
        if published_date_element:
            time_element = published_date_element.find('time')
            if time_element:
                published_date = time_element.text.strip()

        headline_element = article_soup.find('h1', {'class': 'headline speakable'})
        headline = headline_element.text.strip() if headline_element else None

        publisher = "Fox News"  # You can hardcode this since it's constant for all articles from the same source

        article_content = ''
        content_blocks = article_soup.find_all('div', class_='article-body')
        for block in content_blocks:
            paragraphs = block.find_all('p')
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
