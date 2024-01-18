import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

def get_html(urls: list[str]) -> (dict[str, str], int):
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
        else:
            # If the request was not successful, increment the failed_fetch counter
            failed_fetch += 1

        # Split text into lines, filter out empty lines, and join the non-empty lines
        lines = text.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        result = '\n'.join(non_empty_lines)

        # Store the result in the dictionary with the URL as the key
        website_content[website] = result

    return website_content, failed_fetch

# Usecase example:
"""
text2, failed_fetch_html = get_html(["https://timesofindia.indiatimes.com/india/whole-world-waiting-for-22nd-january-pm-modi-in-ayodhya/articleshow/106388185.cms"])
print(text2)
"""

# Note: Uncomment the usecase example when using this code.
