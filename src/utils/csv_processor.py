import csv
from io import StringIO
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_csv_data(csv_data):
    """
    Reads CSV data, filters URLs to keep only 'en' versions, and returns the filtered data.

    Args:
        csv_data (str): CSV data as a string.

    Returns:
        str: Filtered CSV data as a string.
    """
    url_map = {}
    new_rows = []

    csvfile = StringIO(csv_data) #Use StringIO, treat string as a file
    reader = csv.reader(csvfile)
    try:
        header = next(reader)
        if header != ['Parent Sitemap', 'URL']:
            logging.warning(f"Unexpected header in CSV: {header}.  Assuming standard 'Parent Sitemap,URL' format.")
    except StopIteration:
        logging.warning("CSV data is empty.")
        return ""  # Return empty string if CSV is empty


    for row in reader:
        if len(row) != 2:
            logging.warning(f"Skipping row with unexpected number of columns: {row}")
            continue

        parent_sitemap, url = row
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.split('/')

        language_code = path_segments[1] if len(path_segments) > 1 else None

        url_key = '/'.join(path_segments[2:])

        if not language_code:
            new_rows.append([parent_sitemap, url])
            continue

        if url_key not in url_map:
            url_map[url_key] = {'en': None}
            if language_code == 'en':
                url_map[url_key]['en'] = [parent_sitemap, url]
            else:
                url_map[url_key][language_code] = [parent_sitemap, url]

        elif language_code == 'en':
            url_map[url_key]['en'] = [parent_sitemap, url]

        elif 'en' not in url_map[url_key] or url_map[url_key]['en'] is None:
            url_map[url_key][language_code] = [parent_sitemap, url]

    filtered_data = StringIO()
    writer = csv.writer(filtered_data)
    writer.writerow(['Parent Sitemap', 'URL'])

    for url_key in url_map:
        if url_map[url_key]['en'] is not None:
            writer.writerow(url_map[url_key]['en'])
        else:
            for lang in url_map[url_key]:
                if url_map[url_key][lang] is not None:
                    writer.writerow(url_map[url_key][lang])
    return filtered_data.getvalue() #get the string for next func