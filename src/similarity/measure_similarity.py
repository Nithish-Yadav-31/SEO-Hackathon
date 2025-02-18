# Example with cleaned keywords
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_cosine_similarity(keywords1, keywords2):
    """
    Calculates the cosine similarity between two sets of keywords using TF-IDF.

    Args:
        keywords1: A list of strings representing the keywords for the first website.
        keywords2: A list of strings representing the keywords for the second website.

    Returns:
        The cosine similarity score (a float between 0 and 1).
    """

    # Combine the keywords into a single list of strings, where each element is
    # the keywords for one website.
    documents = [" ".join(keywords1), " ".join(keywords2)]

    # Create a TF-IDF vectorizer. This will:
    # 1. Tokenize the strings (split them into words).
    # 2. Count the term frequencies.
    # 3. Calculate the IDF for each term.
    # 4. Calculate the TF-IDF scores.
    vectorizer = TfidfVectorizer()

    # Fit and transform the documents into a TF-IDF matrix.
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Calculate the cosine similarity between the two TF-IDF vectors.
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    return cosine_sim


def clean_keywords(keywords):
  keywords = [word.lower() for word in keywords]
  stop_words = set(stopwords.words('english'))
  keywords = [word for word in keywords if word not in stop_words]
  stemmer = PorterStemmer()
  keywords = [stemmer.stem(word) for word in keywords]
  return keywords

