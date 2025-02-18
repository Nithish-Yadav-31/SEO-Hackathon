# app.py (modified)
from flask import Flask, render_template, request, redirect, url_for
import logging
from io import StringIO, BytesIO
import csv
import os
from urllib.parse import urlparse
import re

# Import the functions from the separate files
import src.utils.sitemap_extractor as sitemap_extractor
import src.utils.csv_processor as csv_processor
import src.spiders.scrapy_spider as scrapy_spider
import src.scraping.get_keywords as get_keywords
import src.scraping.search_competitor as search_competitor
import src.similarity.measure_similarity as measure_similarity
import src.llm_analysis.intent_analyser as intent_analyser
import src.llm_analysis.query_writer as query_writer
import src.llm_analysis.compare_intent as compare_intent  # Import the new compare_intent module
import src.llm_analysis.missing_topic_finder as missing_topic_finder #missing topic finder
import src.similarity.similarity_with_HyDE as similarity_with_HyDE #HyDE similarity

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- Configuration ---
SCRAPY_OUTPUT_FILENAME = "output_scrapy.csv"  # Temporary file name
CSV_ENCODING = 'utf-8'


def create_filename(url):
    """Creates a filename from the website URL."""
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc
    # Remove "www." prefix
    if hostname.startswith("www."):
        hostname = hostname[4:]

    # Get the domain extension (e.g., "com", "net", "org")
    domain_extension = hostname.split(".")[-1]  # or use tldextract library for more accuracy

    # Create safe filename (replace invalid characters with underscores)
    safe_hostname = re.sub(r"[^a-zA-Z0-9_]", "_", hostname.replace("." + domain_extension, ""))  # Also exclude the domain extension when replacing chars to avoid issues
    filename = f"{safe_hostname}_{domain_extension}.csv"

    return filename


def filter_rows_with_meta_keywords(csv_data):
    """
    Filters rows where the 'Meta Keywords' column is empty or null.
    """
    csv_rows = list(csv.reader(StringIO(csv_data)))
    headers = csv_rows[0]
    data = csv_rows[1:]

    # Find the index of the 'Meta Keywords' column
    meta_keywords_index = headers.index("Meta Keywords")

    # Filter rows where 'Meta Keywords' is not empty
    filtered_data = [row for row in data if row[meta_keywords_index].strip()]

    # Combine headers and filtered data
    filtered_csv = StringIO()
    csv_writer = csv.writer(filtered_csv)
    csv_writer.writerow(headers)
    csv_writer.writerows(filtered_data)

    return filtered_csv.getvalue()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        website_url = request.form['website_url']
        return redirect(url_for('process_website', website_url=website_url))
    return render_template('index.html')


@app.route('/process/<path:website_url>', methods=['GET', 'POST'])
def process_website(website_url):
    if request.method == 'POST':
        query = request.form['query']
    else:
        query = None

    # 1. Extract Sitemap URLs
    sitemap_urls = sitemap_extractor.extract_sitemap_urls(website_url)

    if not sitemap_urls:
        return render_template('error.html', message="No sitemap URLs found for this website.")

    # 2. Convert URLs to CSV data (in memory)
    csv_output = StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow(['Parent Sitemap', 'URL'])  # Header
    csv_writer.writerows(sitemap_urls)  # Data
    csv_data = csv_output.getvalue()

    # 3. Process CSV data (filter 'en' URLs)
    filtered_csv_data = csv_processor.process_csv_data(csv_data)

    if not filtered_csv_data:
        return render_template('error.html', message="No URLs remaining after filtering.")

    # 4. Run Scrapy spider directly on the filtered data
    final_csv_data = scrapy_spider.run_scrapy_spider(filtered_csv_data)

    if not final_csv_data:
        return render_template('error.html', message="Error running Scrapy spider.")

    # 5. Filter rows with empty 'Meta Keywords'
    final_csv_data = filter_rows_with_meta_keywords(final_csv_data)

    # 6. Extract top keywords from all Meta Keywords
    website_keywords = get_keywords.top_keywords_from_csv(
        csv_filepath=StringIO(final_csv_data),  # Pass CSV data in memory
        column_name='Meta Keywords'
    )

    # 7. Generate search query using query_writer.py
    search_query = query_writer.search_query_writer(website_keywords)

    # 8. Search competitors and aggregate keywords
    competitor_keywords_string = search_competitor.search_and_aggregate_keywords(search_query)

    if not competitor_keywords_string:
        competitor_keywords = [] #assign an empty list, to avoid error
        logging.warning("No competitor keywords found.") #or handle differently

    else:
        competitor_keywords = [k.strip() for k in competitor_keywords_string.split(",")] #Convert to a list

    website_keywords_list = [k.strip() for k in website_keywords.split()]  #Split into a list

    # 9. Analyze intents
    website_intent = intent_analyser.analyze_intent(website_keywords)
    competitor_intent = intent_analyser.analyze_intent(competitor_keywords_string)

    # 10. Calculate similarity score
    similarity_score = measure_similarity.calculate_cosine_similarity(
        website_keywords_list, competitor_keywords
    )

    # 11. Compare and consolidate intents using compare_intent.py
    overall_intent = compare_intent.compare_intents(competitor_intent, website_intent)

    # 12. Find missing Topics
    missing_topics = missing_topic_finder.find_missing_topics(website_keywords)

    # 13. Run similarity with HyDE paragraphs similarity_with_HyDE.py
    hyde_similarity_score = similarity_with_HyDE.calculate_paragraph_similarity(website_keywords, competitor_keywords_string)
    # 14. Save the final CSV data to a file
    output_filename = create_filename(website_url)  # Generate filename
    try:
        with open(output_filename, 'w', encoding=CSV_ENCODING) as output_file:
            output_file.write(final_csv_data)
        logging.info(f"Saved final CSV data to {output_filename}")
    except Exception as e:
        logging.error(f"Error saving CSV file: {e}")
        return render_template("error.html", message="Error saving CSV file.")

    # 15. Render the template with analysis results
    return render_template(
        'display_csv.html',
        website_url=website_url,
        query=query,
        website_keywords=website_keywords,
        search_query=search_query,
        competitor_keywords=competitor_keywords_string,
        website_intent=website_intent,
        competitor_intent=competitor_intent,
        similarity_score=similarity_score,
        overall_intent=overall_intent,
        missing_topics = missing_topics,
        hyde_similarity_score = hyde_similarity_score
    )


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message="Internal server error. Please check the logs.")


if __name__ == '__main__':
    app.run(debug=True)