import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from flask_socketio import SocketIO,emit
from progress import *

# socketio = SocketIO(app)


def is_english(text):
    """
    Check if the given text contains mostly English characters.
    """
    english_count = sum(1 for char in text if ord(char) < 128)
    non_english_count = len(text) - english_count
    return english_count >= non_english_count

def check_failure(text, failed_txt):
    """
    Check if any of the failure strings exist in the given text.
    """
    return any(failure_str.lower() in text.lower() for failure_str in failed_txt)


def get_html(urls, mode_of_search = None) :
    """
    Function that takes in URLs and returns the HTML content within them.

    Args:
    urls: List of all URLs.

    Returns:
    website_content: Dictionary {url: html_content}.
    failed_fetch: Number of websites that couldn't be accessed during fetching HTML.
    """

    website_content = {}  # Dictionary to store HTML content for each URL
    failed_fetch = 0  # Counter for failed fetch attempts

    failed_txt = ["Sorry", "not found", "oops", "try again", "failed", "error"]
    items_completed = 0
    total_items = len(urls)
    num_of_output_progress = 10
    # Iterate through each URL in the list
    for website_idx in tqdm(range(len(urls))):
        website = urls[website_idx]

        # Send an HTTP GET request to the website
        response = requests.get(website)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()

            # Check if the text contains mostly English characters
            if is_english(text):
                # Split text into lines, filter out empty lines, and join the non-empty lines
                lines = text.splitlines()
                non_empty_lines = [line for line in lines if line.strip()]
                result = '\n'.join(non_empty_lines)

                if mode_of_search == "Search Bar Scrape":
                    if check_failure(result, failed_txt):
                        pass
                    else:
                        website_content[website] = result
                else:
                    # Store the result in the dictionary with the URL as the key
                    website_content[website] = result
            else:
                pass  # Not saving non-English content
        else:
            # If the request was not successful, increment the failed_fetch counter
            failed_fetch += 1

        items_completed += 1
        try:
            if items_completed % (total_items // num_of_output_progress) == 0:
                percentage_complete = (items_completed / total_items) * 100
                socketio.emit('print_output', {'output': f"{progress_bar_once(word='Completed', percentage=round(percentage_complete, 2), num=30)}"})
        except: pass

    return website_content, failed_fetch

# Usecase example:
"""
text2, failed_fetch_html = get_html(["https://timesofindia.indiatimes.com/india/whole-world-waiting-for-22nd-january-pm-modi-in-ayodhya/articleshow/106388185.cms"])
print(text2)
"""

# Note: Uncomment the usecase example when using this code.
