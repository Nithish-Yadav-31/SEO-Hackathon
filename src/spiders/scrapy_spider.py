# scrapy_spider.py
import scrapy
from io import StringIO
import csv
import logging
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor  # Import reactor
import re
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCRAPY_OUTPUT_FILENAME = "output_scrapy.csv"
CSV_ENCODING = 'utf-8'

class TopicSpider(scrapy.Spider):
    name = "topic_spider"
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': SCRAPY_OUTPUT_FILENAME,
        'FEED_EXPORT_ENCODING': CSV_ENCODING, # Ensure correct encoding
        'FEED_FIELDS': ['Parent Sitemap', 'URL', 'Topic', 'Meta Description', 'Meta Keywords', 'Meta Robots', 'Meta Author'], #Define the order
        'overwrite': True,
    }

    def __init__(self, csv_data=None, *args, **kwargs):  # takes csv DATA as an argument not FILE
        super(TopicSpider, self).__init__(*args, **kwargs)
        if csv_data is None:
            raise ValueError("Please provide CSV data to the spider.")
        self.csv_data = csv_data
        self.start_urls = []
        self.url_topic_mapping = {}

        # Using StringIO again
        csvfile = StringIO(self.csv_data)
        reader = csv.DictReader(csvfile)
        self.fieldnames = reader.fieldnames  # Store fieldnames
        for row in reader:
            url = row.get('URL')
            if url:
                self.start_urls.append(url)
                self.url_topic_mapping[url] = row

    def parse(self, response):
        url = response.url
        meta_description = response.xpath('//meta[@name="description"]/@content').get()
        meta_keywords = response.xpath('//meta[@name="keywords"]/@content').get()
        meta_robots = response.xpath('//meta[@name="robots"]/@content').get()
        meta_author = response.xpath('//meta[@name="author"]/@content').get()
        topic = response.xpath('//title/text()').get()

        # Get the corresponding row from the CSV data
        row = self.url_topic_mapping.get(url, {})

        yield {
            'Parent Sitemap': row.get('Parent Sitemap', ''), # Get parent sitemap
            'URL': url,
            'Topic': topic,
            'Meta Description': meta_description,
            'Meta Keywords': meta_keywords,
            'Meta Robots': meta_robots,
            'Meta Author': meta_author
        }
        
def run_scrapy_spider(csv_data):
    """Runs the Scrapy spider and returns the final CSV data."""
    process = CrawlerProcess()

    # Remove any existing file first
    if os.path.exists(SCRAPY_OUTPUT_FILENAME):
       os.remove(SCRAPY_OUTPUT_FILENAME)

    process.crawl(TopicSpider, csv_data=csv_data)
    process.start()  # the script will block here until the crawling is finished

    # Read the data from the file
    try:
        with open(SCRAPY_OUTPUT_FILENAME, 'r', encoding=CSV_ENCODING) as f:
            final_csv_data = f.read()
    except Exception as e:
        logging.error(f"Error reading Scrapy output file: {e}")
        return None

    return final_csv_data