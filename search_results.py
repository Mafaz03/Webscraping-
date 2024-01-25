import re
import requests
from tqdm import tqdm

def check_url_existence(url):
    """
    Check the existence of a URL by sending a HEAD request.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL exists and returns a 200 status code, False otherwise.
    """
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def get_final_url(url):
    """
    Get the final URL after following redirects.

    Args:
        url (str): The original URL.

    Returns:
        str or None: The final URL after following redirects, or None if an error occurs.
    """
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except requests.ConnectionError:
        return None

def generate_urls_with_exclusions(base_urls, search_extras, keywords, excluded_domains):
    """
    Generate URLs by combining base URLs with search extras and keywords, excluding specified domains.

    Args:
        base_urls (list): List of base URLs.
        search_extras (list): List of search bar extras.
        keywords (list): List of keywords.
        excluded_domains (str): Regular expression pattern for excluded domains.

    Returns:
        set: Set of valid URLs that pass the existence check and do not contain excluded domains.
    """
    excluded_domains_pattern = re.compile(excluded_domains)
    available_urls = set()
    

    for url in tqdm(base_urls):
        for extra in tqdm(search_extras):
            for keyword in keywords:
                possible_link = url + extra + keyword

                if check_url_existence(possible_link) and not excluded_domains_pattern.search(possible_link):
                    # if get_html([url]) != get_html([possible_link]):
                    available_urls.add(possible_link)
                    break  # Move to the next base_url

                else:
                    redirected_link = get_final_url(possible_link)
                    if redirected_link is not None and not excluded_domains_pattern.search(redirected_link):
                        # if get_html([url]) != get_html([possible_link]):
                        available_urls.add(redirected_link)
                        

    return available_urls


def check_failure(text, failed_txt):
    return any(failure_str.lower() in text.lower() for failure_str in failed_txt)

"""
# Example usage:
result_text = "The operation failed with an error. Please try again."
failed_txt = ["Sorry", "not found", "oops", "try again", "failed", "error"]

if check_failure(result_text, failed_txt):
    print("Failure detected!")
else:
    print("No failure.")
"""