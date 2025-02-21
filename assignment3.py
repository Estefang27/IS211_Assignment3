import argparse
import urllib.request
import csv
import re
from collections import Counter, defaultdict
from datetime import datetime


IMAGE_REGEX = re.compile(r'\.(jpg|gif|png)$', re.IGNORECASE)
BROWSER_REGEX = re.compile(r'(Firefox|Chrome|Safari|MSIE)')


def download_data(url):
    """Download the data from the provided URL"""
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading the data: {e}")
        exit(1)


def process_data(data):
    """Process the CSV data and return necessary stats"""
    csv_reader = csv.reader(data.splitlines())

    total_hits = 0
    image_hits = 0
    browser_counter = Counter()
    hourly_hits = defaultdict(int)

    for row in csv_reader:
        if len(row) < 5:
            continue  # Skip malformed rows
        path, datetime_accessed, user_agent, status, size = row

        # Increment total hit counter
        total_hits += 1

        # Check if the path corresponds to an image
        if IMAGE_REGEX.search(path):
            image_hits += 1

        # Extract browser info from User-Agent
        browser_match = BROWSER_REGEX.search(user_agent)
        if browser_match:
            browser_counter[browser_match.group(0)] += 1

        # Extract hour from datetime and count hits per hour
        try:
            dt_obj = datetime.strptime(datetime_accessed, "%m/%d/%Y %H:%M:%S")
            hour = dt_obj.hour
            hourly_hits[hour] += 1
        except ValueError:
            pass  # Ignore malformed datetime entries

    return total_hits, image_hits, browser_counter, hourly_hits


def display_image_stats(total_hits, image_hits):
    """Display the percentage of image hits"""
    if total_hits == 0:
        print("No hits found.")
    else:
        image_percentage = (image_hits / total_hits) * 100
        print(f"Image requests account for {image_percentage:.2f}% of all requests")


def display_most_popular_browser(browser_counter):
    """Display the most popular browser"""
    if browser_counter:
        most_common_browser = browser_counter.most_common(1)[0]
        print(f"The most popular browser is {most_common_browser[0]} with {most_common_browser[1]} hits")
    else:
        print("No browser information available.")


def display_hourly_hits(hourly_hits):
    """Display the total hits per hour, sorted by hour"""
    for hour in sorted(hourly_hits.keys()):
        print(f"Hour {hour:02d} has {hourly_hits[hour]} hits")


def main(url):
    # Download and process the data
    data = download_data(url)
    total_hits, image_hits, browser_counter, hourly_hits = process_data(data)

    # Display statistics
    display_image_stats(total_hits, image_hits)
    display_most_popular_browser(browser_counter)
    display_hourly_hits(hourly_hits)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to the datafile", type=str, required=True)
    args = parser.parse_args()
    main(args.url)
