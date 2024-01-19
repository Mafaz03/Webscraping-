import re
import requests

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
    

    for url in base_urls:
        for extra in search_extras:
            for keyword in keywords:
                possible_link = url + extra + keyword

                if check_url_existence(possible_link) and not excluded_domains_pattern.search(possible_link):
                    available_urls.add(possible_link)
                else:
                    redirected_link = get_final_url(possible_link)
                    if redirected_link is not None and not excluded_domains_pattern.search(redirected_link):
                        available_urls.add(redirected_link)

    return available_urls

"""
# Example usage:
base_urls = ["https://www.postcourier.com.pg", "https://www.africanews.com", "https://www.khaleejtimes.com", "http://bbc.com"]
search_extras = ["?s=", "/search/", "/search?q=", "/topic/"]
keywords = ["png", "road"]
excluded_domains = r'(magicbricks|play\.google|facebook\.com|twitter\.com|instagram\.com|linkedin\.com|youtube\.com|\.gov|\.org|policy|terms|buy|horoscope|web\.whatsapp\.com|\.(png|jpg|jpeg|gif|bmp|tiff|webp))'

result_urls = generate_urls_with_exclusions(base_urls, search_extras, keywords, excluded_domains)
print(result_urls)
"""