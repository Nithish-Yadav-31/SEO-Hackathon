import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import re
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


ALLOWED_COUNTRIES = {"US", "SA", "QA", "IN", "KR", "CN", "SG", "AU"}
MIN_URL_THRESHOLD = 100
MAX_RECURSION_DEPTH = 5  # Define maximum recursion depth

ROBOTS_DIR = "robots"  # Directory to save robots.txt files


def create_csv_filename(url):
    """
    Creates a safe CSV filename from a URL.
    """
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc

    # Remove "www." prefix, if present
    if hostname.startswith("www."):
        hostname = hostname[4:]

    # Replace invalid characters with underscores
    safe_hostname = re.sub(r"[^a-zA-Z0-9_]", "_", hostname)

    # Truncate if the name is too long
    max_length = 200  # Maximum filename length (adjust as needed)
    if len(safe_hostname) > max_length:
        safe_hostname = safe_hostname[:max_length]

    # Ensure the filename is not empty
    if not safe_hostname:
        safe_hostname = "default_sitemap"

    return f"{safe_hostname}.csv"


def get_sitemap_url_from_robots(robots_txt):
    """
    Extracts the sitemap URL from a robots.txt file using regular expressions.

    Args:
        robots_txt (str): The content of the robots.txt file.

    Returns:
        str: The sitemap URL, or None if not found.
    """
    pattern = re.compile(r"^Sitemap:\s*(.*)$", re.IGNORECASE | re.MULTILINE)  # Regex pattern
    match = pattern.search(robots_txt)
    if match:
        return match.group(1).strip()
    return None

def extract_country_code(url):
    """
    Extracts the country code from a URL if it matches the pattern '-en-<country>'

    Args:
        url (str): The URL to extract the country code from.

    Returns:
        str: The country code in uppercase, or None if not found.
    """
    match = re.search(r"-en-([a-z]{2})", url, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

def get_base_url(url):
    """
    Extracts the base URL (scheme and netloc) from a given URL.

    Args:
        url (str): The URL to extract the base URL from.

    Returns:
        str: The base URL.
    """
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def extract_sitemap_urls(url):
    """
    Extracts URLs from a sitemap.xml or a sitemap URL found in robots.txt and returns them.

    Args:
        url (str): The base URL of the website.

    Returns:
        list: A list of tuples (parent_sitemap, URL) or None on error.
    """

    base_url = get_base_url(url)
    logging.info(f"Using base URL: {base_url}")

    all_urls = []
    visited_sitemaps = set()
    parent_sitemap = None

    # 1. Try /sitemap.xml
    try:
        sitemap_url = urljoin(base_url, "sitemap.xml")
        logging.info(f"Trying sitemap.xml: {sitemap_url}")
        response = requests.get(sitemap_url, timeout=15)
        response.raise_for_status()
        parent_sitemap = sitemap_url

        if response.status_code == 200:
            all_urls.extend(parse_sitemap_xml(response.content, visited_sitemaps=visited_sitemaps, parent_sitemap=parent_sitemap))
            if all_urls:
                logging.info(f"Found URLs in sitemap.xml")
            else:
                logging.info(f"No URLs found in sitemap.xml (but it exists).")
        else:
            logging.warning(f"sitemap.xml returned status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        logging.info(f"Error accessing sitemap.xml: {e}")

    # 2. Try /robots.txt
    try:
        robots_url = urljoin(base_url, "robots.txt")
        logging.info(f"Trying robots.txt: {robots_url}")
        response = requests.get(robots_url, timeout=15)
        response.raise_for_status()

        if response.status_code == 200:
            # Save robots.txt content to a file
            hostname = urlparse(base_url).netloc
            filename = f"robots_{hostname}.txt"
            filepath = os.path.join(ROBOTS_DIR, filename)

            # Ensure the 'robots' directory exists
            os.makedirs(ROBOTS_DIR, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            logging.info(f"robots.txt saved to {filepath}")

            sitemap_from_robots = get_sitemap_url_from_robots(response.text)
            if sitemap_from_robots:
                if not urlparse(sitemap_from_robots).scheme:
                    sitemap_from_robots = urljoin(base_url, sitemap_from_robots)

                logging.info(f"Found sitemap URL in robots.txt: {sitemap_from_robots}")

                if sitemap_from_robots in visited_sitemaps:
                    logging.warning(f"Skipping already visited sitemap: {sitemap_from_robots}")
                else:
                    try:
                        response = requests.get(sitemap_from_robots, timeout=15)
                        response.raise_for_status()
                        parent_sitemap = sitemap_from_robots

                        if response.status_code == 200:
                            all_urls.extend(parse_sitemap_xml(response.content, visited_sitemaps=visited_sitemaps, parent_sitemap=parent_sitemap))
                            if all_urls:
                                logging.info(f"Found URLs in sitemap from robots.txt")
                            else:
                                logging.info(f"No URLs found in sitemap from robots.txt (but it exists).")
                        else:
                            logging.warning(f"Sitemap from robots.txt returned status code: {response.status_code}")

                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error accessing sitemap URL from robots.txt: {e}")
            else:
                logging.info("No sitemap URL found in robots.txt")
        else:
            logging.warning(f"robots.txt returned status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        logging.info(f"Error accessing robots.txt: {e}")

    # Explicitly handle the case where the robots.txt fetch fails but we *still* have a sitemap URL from it
    if not all_urls:
        try:
            robots_url = urljoin(base_url, "robots.txt")
            response = requests.get(robots_url, timeout=15)
            sitemap_from_robots = get_sitemap_url_from_robots(response.text)
            if sitemap_from_robots:
                try:
                    response = requests.get(sitemap_from_robots, timeout=15)  # Add timeout
                    response.raise_for_status()
                    parent_sitemap = sitemap_from_robots

                    if response.status_code == 200:

                        all_urls.extend(
                            parse_sitemap_xml(response.content, visited_sitemaps=visited_sitemaps,
                                              parent_sitemap=parent_sitemap))  # Accumulate URLs
                        if all_urls:
                            logging.info(f"Found URLs in sitemap from robots.txt")
                        else:
                            logging.info(f"No URLs found in sitemap from robots.txt (but it exists).")
                    else:
                        logging.warning(f"Sitemap from robots.txt returned status code: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    logging.error(f"Error accessing sitemap URL from robots.txt: {e}")

        except:
            logging.info("No sitemap found.")
            return None

    if not all_urls:
        logging.info("No sitemap found.")
        return None

    return all_urls  # Return the list of URLs


def parse_sitemap_xml(xml_content, depth=0, max_depth=MAX_RECURSION_DEPTH, visited_sitemaps=None, parent_sitemap=None):
    """
    Parses an XML sitemap and extracts the URLs. Handles both standard sitemap and sitemap index files.
    Prioritizes extracting 'en' URLs.

    Args:
        xml_content (bytes): The XML content of the sitemap.
        depth (int): The current recursion depth.
        max_depth (int): The maximum recursion depth allowed.
        visited_sitemaps (set): A set to keep track of visited sitemap URLs.
        parent_sitemap (str): URL of the parent sitemap.

    Returns:
        list: A list of tuples (parent_sitemap, URL) found in the sitemap.
    """

    if visited_sitemaps is None:
        visited_sitemaps = set()

    if depth > max_depth:
        logging.warning(f"Max recursion depth ({max_depth}) reached. Skipping this sitemap.")
        return []

    urls = []
    try:
        root = ET.fromstring(xml_content)

        # Count total URL elements
        total_url_count = len(root.findall('.//{*}url'))
        logging.info(f"Total URL count in sitemap: {total_url_count}, parent {parent_sitemap}")

        # First, extract all the 'en' URLs
        en_urls = []
        for element in root.findall('.//{*}url'):
            loc_element = element.find('.//{*}loc')
            if loc_element is not None:
                url_value = loc_element.text

                # Skip media URLs that are clustered together
                if re.search(r"\.(jpg|jpeg|png|gif|webp)$", url_value):  # Basic media extension check
                    logging.info(f"Skipping media URL: {url_value}")
                    continue

                # Skip if the urls clustered together, aka more than one slash
                if url_value.count('/') > 50:
                    logging.info(f"Skipping clustered media URL: {url_value}")
                    continue

                if 'en' in url_value:  # Check for 'en' in the URL
                    en_urls.append((parent_sitemap, url_value))

        # If we found any 'en' URLs, use them. Otherwise, fall back to all URLs.
        if en_urls:
            logging.info("Found 'en' URLs, processing only those.")
            urls = en_urls
        else:
            logging.info("No 'en' URLs found, processing all URLs.")
            for element in root.findall('.//{*}url'):  # handles standard sitemaps
                loc_element = element.find('.//{*}loc')
                if loc_element is not None:
                    url_value = loc_element.text

                    # Skip media URLs that are clustered together
                    if re.search(r"\.(jpg|jpeg|png|gif|webp)$", url_value):  # Basic media extension check
                        logging.info(f"Skipping media URL: {url_value}")
                        continue

                    # Skip if the urls clustered together, aka more than one slash
                    if url_value.count('/') > 50:
                        logging.info(f"Skipping clustered media URL: {url_value}")
                        continue

                    urls.append((parent_sitemap, url_value))  # Add Parent here

        # Handle sitemap index files separately

        for element in root.findall('.//{*}sitemap'):  # handles sitemapindex

            loc_element = element.find('.//{*}loc')
            if loc_element is not None:
                sitemap_url = loc_element.text  # Store the URL

                # Check if we've already visited this sitemap URL
                if sitemap_url in visited_sitemaps:
                    logging.warning(f"Skipping already visited sitemap: {sitemap_url}")
                    continue  # Skip to the next sitemap

                # 3rd Condition
                if 'en' in sitemap_url:
                    try:
                        logging.info(f"Accessing sub-sitemap: {sitemap_url}")
                        sub_response = requests.get(sitemap_url, timeout=15)  # Add timeout
                        sub_response.raise_for_status()

                        visited_sitemaps.add(sitemap_url)  # Mark sitemap as visited BEFORE parsing
                        urls.extend(parse_sitemap_xml(sub_response.content, depth=depth + 1, max_depth=max_depth,
                                                      visited_sitemaps=visited_sitemaps, parent_sitemap=sitemap_url))  # recursive call if nested sitemap
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error accessing sub-sitemap {sitemap_url}: {e}")
                else:
                    logging.info(f"Skipping sitemap (no 'en'): {sitemap_url}")


    except ET.ParseError as e:
        logging.error(f"Error parsing sitemap XML: {e}")

    return urls