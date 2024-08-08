import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import seaborn as sns
import matplotlib.pyplot as plt
from dateutil import parser
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split, StratifiedKFold
import joblib


# Define a function to handle unknown timezones
def custom_parser(date_string):
    try:
        return parser.parse(date_string)
    except:
        return parser.parse(date_string, tzinfos={"EDT": -14400})


# Download NLTK resources (run only once)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def create_df():
    # Read the CSV files
    nbc_df = pd.read_csv("nbc_news_articles.csv")
    news_df = pd.read_csv("bbc_news_articles.csv")
    fox_df = pd.read_csv("fox_news_articles.csv")

    # Concatenate the dataframes
    df = pd.concat([nbc_df, news_df, fox_df], ignore_index=True)

    # Write the concatenated dataframe to a new CSV file
    df.to_csv("news_articles.csv", index=False)

    missing_values = df.isnull().sum()
    print("Missing Values:\n", missing_values)

    # Drop all rows with missing values
    df = df.dropna()

    # Define the pattern to match in the headline
    pattern = "NBC Affiliates,NBC News,\"WVTM Birmingham, AL www.wvtm13.com"

    # Filter rows where the headline contains the specified pattern
    filtered_df = df[~df['headline'].str.contains(pattern)]

    # Reset index after filtering rows
    filtered_df.reset_index(drop=True, inplace=True)

    # Shuffle the dataset
    shuffled_df = filtered_df.sample(frac=1, random_state=42)  # Shuffle all rows, random_state for reproducibility

    # Reset index after shuffling
    shuffled_df.reset_index(drop=True, inplace=True)

    # Write the shuffled dataset to a new CSV file
    shuffled_df.to_csv("filtered_news_articles.csv", index=False)

    # Print the shuffled dataset information
    print(shuffled_df.info())

    return shuffled_df


def preprocess_text(text):
    # Remove special characters
    reviews = ''.join([x if x.isalnum() else ' ' for x in text])

    # Convert text to lowercase
    reviews = reviews.lower()

    # Tokenize the text
    words = word_tokenize(reviews)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [x for x in words if x not in stop_words]

    # Lemmatize words
    wordnet = WordNetLemmatizer()
    words = [wordnet.lemmatize(word) for word in words]

    # Join the words back into a single string
    preprocessed_text = ' '.join(words)

    return preprocessed_text


df = create_df()

while True:
    print("Select the following options: ")
    print("1. Preprocess the data")
    print("2. Conduct EDA after the preprocessing of the data")
    print("3. Build model")
    print("4. Exit the program")

    selection = input("Enter your choice: ")

    if selection == "1":
        # Apply text preprocessing to 'article_content' column
        df['article_content_processed'] = df['article_content'].apply(preprocess_text)
        # Apply text preprocessing to 'headline' column
        df['headline_processed'] = df['headline'].apply(preprocess_text)
        # Print the preprocessed text data
        print(df[['article_content_processed', 'headline_processed']].head())

        category_mapping = {
            r'\btech\b': 'Technology',
            r'\bTech\b': 'Technology',
            r'\bWorld-Us-Canada\b': 'Us_News',
            r'\bUs\b(?!\-News)': 'Us_News',  # Match 'Us' as a standalone word, not followed by '-News'
            r'\bUs-News\b': 'Us_News',
            r'\bScience-Environment\b': 'Technology',
            r'\bEntertainment-Arts\b': 'Entertainment'
        }

        df['category'] = df['category'].replace(category_mapping, regex=True)
        target_category = df['category'].unique()
        print(target_category)
        df['category_id'] = df['category'].factorize()[0]
        df.head()

        # Store the preprocessed data into a new CSV file
        df.to_csv("preprocessed_dataset.csv", index=False)

    elif selection == "2":
        # Load the dataset
        df = pd.read_csv("preprocessed_dataset.csv", parse_dates=['published_date'], date_parser=custom_parser)

        # Summary Statistics
        print("Summary Statistics:")
        print(df.describe())

        df['category'].value_counts()

        plt.figure(figsize=(8, 5))
        sns.countplot(data=df, x='publisher')
        plt.title('Publisher Distribution')
        plt.xticks(rotation=45)
        plt.show()

        plt.figure(figsize=(10, 6))
        sns.histplot(df['category'], bins=20, kde=True)
        plt.title('Category Distribution')
        plt.xlabel('Category')
        plt.ylabel('Frequency')
        plt.show()

        fig = plt.figure(figsize=(5, 5))
        colors = ["skyblue"]
        Sports = df[df['category_id'] == 0]
        Health = df[df['category_id'] == 1]
        Business = df[df['category_id'] == 2]
        Us_News = df[df['category_id'] == 3]
        Entertainment = df[df['category_id'] == 4]
        Politics = df[df['category_id'] == 5]
        Technology = df[df['category_id'] == 6]
        count = [Sports['category_id'].count(), Health['category_id'].count(), Business['category_id'].count(),
                 Us_News['category_id'].count(), Entertainment['category_id'].count(), Politics['category_id'].count(),
                 Technology['category_id'].count()]
        pie = plt.pie(count,
                      labels=['Sports', 'Health', 'Business', 'Us_News', 'Entertainment', 'Politics', 'Technology'],
                      autopct="%1.1f%%",
                      shadow=True,
                      colors=colors,
                      startangle=45,
                      explode=(0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05))
        plt.show()
    elif selection == "3":
        dataset = pd.read_csv("preprocessed_dataset.csv", parse_dates=['published_date'], date_parser=custom_parser)
        x = dataset['article_content_processed']
        y = dataset['category_id']
        x = np.array(dataset.iloc[:, 0].values)
        y = np.array(dataset.category_id.values)
        cv = CountVectorizer(max_features=5000)
        x = cv.fit_transform(dataset.article_content_processed).toarray()

        print("X.shape = ", x.shape)
        print("y.shape = ", y.shape)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0, shuffle=True)
        print(len(x_train))
        print(len(x_test))
        # Build and train the logistic regression model
        logistic_model = LogisticRegression(class_weight='balanced')
        logistic_model.fit(x_train, y_train)

        # Make predictions on the test set
        y_pred = logistic_model.predict(x_test)

        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)

        # Get precision, recall, f1-score
        precision, recall, f1score, _ = precision_recall_fscore_support(y_test, y_pred, average='micro')

        joblib.dump(logistic_model, 'logistic_regression_model.pkl')
        # Initialize StratifiedKFol
        kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        # Initialize lists to store evaluation metrics
        accuracies = []
        precisions = []
        recalls = []
        f1_scores = []

        # Perform cross-validation
        for train_index, test_index in kfold.split(x, y):
            X_train, X_test = x[train_index], x[test_index]
            y_train, y_test = y[train_index], y[test_index]

            # Build and train the logistic regression model
            logistic_model = LogisticRegression(class_weight='balanced')
            logistic_model.fit(X_train, y_train)

            # Make predictions on the test set
            y_pred = logistic_model.predict(X_test)

            # Calculate evaluation metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1_score, _ = precision_recall_fscore_support(y_test, y_pred, average='micro')

            # Append metrics to lists
            accuracies.append(accuracy)
            precisions.append(precision)
            recalls.append(recall)
            f1_scores.append(f1_score)

        # Calculate mean metrics
        mean_accuracy = np.mean(accuracies)
        mean_precision = np.mean(precisions)
        mean_recall = np.mean(recalls)
        mean_f1_score = np.mean(f1_scores)

        # Print mean metrics
        print("Mean Accuracy:", mean_accuracy)
        print("Mean Precision:", mean_precision)
        print("Mean Recall:", mean_recall)
        print("Mean F1-score:", mean_f1_score)
    elif selection == "4":
        print("Exiting the program")
        break
    else:
        print("Invalid choice, pls enter your choice again(1, 2, 3)")
