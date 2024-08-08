##### **News Classifier**
This project aims to scrape data from three news publishers, preprocess the text data, analyze it, and train a machine learning model to predict the category of news articles. The tools and libraries used include Selenium WebDriver, Beautiful Soup, NLTK, scikit-learn, and various others for data manipulation and visualization.

### **Table of Contents**
Prerequisites
Installation
Data Scraping
Data Preprocessing
Data Analysis
Model Training
Prediction
Results
Usage

### **Prerequisites**
Python
WebDriver compatible with your browser (e.g., ChromeDriver for Google Chrome)
The following Python libraries:
numpy
pandas
nltk
seaborn
matplotlib
dateutil
scikit-learn
joblib
selenium
beautifulsoup4
Installation
Clone the repository:

git clone https://github.com/YuLeWong2002/News-Classifier.git
Install the required libraries:

pip install numpy pandas nltk seaborn matplotlib python-dateutil scikit-learn joblib selenium beautifulsoup4
Download the WebDriver for your browser and place it in a directory included in your system's PATH.

### **Data Scraping**
The first step is to scrape the news articles from three different publishers. You will need to use Selenium WebDriver to navigate the websites and Beautiful Soup to parse the HTML and extract the relevant data.

### **Data Preprocessing**
Before training the model, we need to preprocess the text data. This includes tokenization, removing stop words, and lemmatization. NLTK library is used for these preprocessing steps.

### **Data Analysis**
Analyze the data to understand its distribution and characteristics. Visualization libraries like Seaborn and Matplotlib are used to plot the distribution of news categories.

### **Model Training**
Train a machine learning model to predict the category of news articles. The scikit-learn library is used for vectorizing the text data and training a logistic regression model.

### **Prediction**
Load the trained model and predict the category of new news articles. You will preprocess the new articles and use the trained model to make predictions.

### **Results**
Evaluate the performance of the model on the test set by calculating metrics such as accuracy, precision, recall, and F1-score.

### **Usage**
Scrape the news data using the provided script.
Preprocess the text data.
Train the model using the training script.
Use the model to predict the category of new news articles.
