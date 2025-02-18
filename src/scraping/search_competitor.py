import re
from bs4 import BeautifulSoup
import requests
from duckduckgo_search import DDGS

def scrape_keywords(url):
    """
    Scrapes metadata keywords or content keywords from a URL.

    Args:
        url: The URL to scrape.

    Returns:
        A list of keywords (strings), or None if no keywords were found.
    """
    try:
        response = requests.get(url, timeout=10)  # Add timeout to prevent hanging
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to get keywords from meta tag
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            keywords = meta_keywords.get("content")
            if keywords:
                return [k.strip() for k in keywords.split(",")]

        # If no meta keywords, extract common words from page content
        text = soup.get_text()
        words = re.findall(r'\b\w+\b', text.lower())  # Extract words, convert to lowercase
        word_counts = {}
        for word in words:
            if len(word) > 3 and word not in stop_words and not re.search(r'\d', word): # Ignore short words, stop words and numeric words
                word_counts[word] = word_counts.get(word, 0) + 1

        # Get the most frequent words as keywords
        sorted_words = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)
        content_keywords = [word for word, count in sorted_words] #Get all of the words

        if content_keywords:
            return content_keywords

        return None # No keywords found

    except requests.exceptions.RequestException as e:
        print(f"Error fetching or processing {url}: {e}")
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def search_and_aggregate_keywords(query, num_results=50):
    """
    Performs a DuckDuckGo search, retrieves the top results, and aggregates
    the top 25 most frequent keywords into a single string.

    Args:
        query: The search query.
        num_results: The number of top results to fetch and scrape.

    Returns:
        A single string containing the top 25 most frequent keywords,
        separated by commas.  Returns an empty string if any error occurs
        during the process or if no keywords are found.
    """

    all_keywords = []
    try:
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=num_results))

            for result in search_results:
                url = result.get('href')  # Correct key to access URL
                if url:
                    keywords = scrape_keywords(url)
                    if keywords:
                        all_keywords.extend(keywords)  # Add keywords to the overall list
                    else:
                        print(f"No keywords found for {url}")
                else:
                    print("URL not found in result.")

        # Count keyword frequencies across all pages
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

        # Get the top 25 most frequent keywords
        sorted_keywords = sorted(keyword_counts.items(), key=lambda item: item[1], reverse=True)
        top_25_keywords = [keyword for keyword, count in sorted_keywords[:25]]

        return ", ".join(top_25_keywords) # Join the keywords into a single string

    except Exception as e:
        print(f"An error occurred during the search: {e}")
        return ""

# Stop words for extracting content based keywords (common words to ignore)
stop_words = set([
    "the", "and", "is", "are", "of", "a", "an", "in", "to", "it", "on",
    "that", "this", "with", "for", "as", "be", "by", "not", "or",
    "but", "from", "at", "you", "your", "can", "they", "their", "he",
    "she", "his", "her", "its", "we", "us", "our", "about", "all", "also",
    "been", "has", "have", "had", "more", "than", "then", "so", "such",
    "was", "were", "will", "would", "should", "could", "would", "him",
    "said", "very", "get", "one", "other", "would", "into", "like",
    "just", "out", "these", "those", "much", "many", "over", "even",
    "only", "most", "some", "any", "made", "make", "making", "through",
    "after", "first", "second", "third", "while", "because", "become",
    "becoming", "both", "each", "every", "until", "whether", "where",
    "which", "who", "how", "why", "when", "what", "there", "here"
])

