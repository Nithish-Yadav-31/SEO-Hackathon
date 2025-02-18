import csv
import re
from nltk.corpus import stopwords
import nltk
from collections import Counter
from io import StringIO

# Download NLTK stopwords if not already downloaded
nltk.download('stopwords', quiet=True)

def top_keywords_from_csv(csv_filepath, column_name, num_keywords=25):
    """
    Reads a CSV file (or StringIO object), extracts text from a specified column,
    cleans the keywords, and returns a single string of the top N unique cleaned keywords.

    Args:
        csv_filepath (str): The path to the CSV file.
        column_name (str): The name of the column to analyze.
        num_keywords (int): The number of top keywords to return. Defaults to 25.

    Returns:
        str: A single string containing the top N unique cleaned keywords, separated by spaces.
             Returns an empty string if the column is not found or if an error occurs.
    """

    try:
        # Check if csv_filepath is a string (file path) or a StringIO object
        if isinstance(csv_filepath, str):
            with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
        else:  # Assume it's a StringIO object
            csvfile = csv_filepath
            reader = csv.DictReader(csvfile)

        if column_name not in reader.fieldnames:
            print(f"Error: Column '{column_name}' not found in the CSV file.")
            return ""

        text_data = []
        for row in reader:
            text = row[column_name]
            if text:
                text_data.append(text)

        # Combine all text into a single string
        all_text = ' '.join(text_data)

        # Tokenize the text into keywords
        keywords = all_text.split()

        # Clean keywords
        cleaned_keywords = clean_keywords(keywords)

        # Count keyword frequencies
        keyword_counts = Counter(cleaned_keywords)

        # Get the top N keywords
        top_keywords = [keyword for keyword, count in keyword_counts.most_common(num_keywords)]

        # Ensure uniqueness while preserving order of top keywords
        unique_top_keywords = []
        seen = set()
        for keyword in top_keywords:
            if keyword not in seen:
                unique_top_keywords.append(keyword)
                seen.add(keyword)

        # Return a single string of unique top keywords
        return " ".join(unique_top_keywords)

    except FileNotFoundError:
        print(f"Error: File not found at '{csv_filepath}'")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def clean_keywords(keywords):
    """
    Cleans a list of keywords by removing stopwords and words with special characters.

    Args:
        keywords (list): A list of keywords to clean.

    Returns:
        list: A list of cleaned keywords.
    """
    # Get English stopwords
    stop_words = set(stopwords.words('english'))

    # Define a regex pattern to match words with special characters
    special_char_pattern = re.compile(r'[^a-zA-Z0-9]')

    cleaned_keywords = []
    for word in keywords:
        # Convert to lowercase
        word_lower = word.lower()

        # Remove stopwords and words with special characters
        if word_lower not in stop_words and not special_char_pattern.search(word_lower):
            cleaned_keywords.append(word_lower)

    return cleaned_keywords