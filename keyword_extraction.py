from tqdm import tqdm

def keyword_extractor_paragraph(website_content: dict[str, str], keywords: list, filter_by_amount: int = None):
    """
    Extracts paragraphs containing specified keywords from website content.

    Args:
    website_content (dict): Dictionary with URLs and corresponding HTML content.
    keywords (list): List of keywords to search for.
    filter_by_amount (int): If the HTML content length is greater than this, keep the content.

    Returns:
    website_content_relevant (dict): Dictionary with URLs and keyword-extracted HTML content.
    """
    website_content_relevant = {}

    for url, text in tqdm(website_content.items()):
        # Split text into lines and remove empty elements
        list_of_split = text.split('\n')
        non_empty_list = [element for element in list_of_split if element != ""]

        # Conditionally filter elements based on keywords and length
        if filter_by_amount is not None:
            result_list = [element for element in non_empty_list if any(keyword.lower() in element.lower() for keyword in keywords) and len(element) > 60]
        else:
            result_list = [element for element in non_empty_list if any(keyword.lower() in element.lower() for keyword in keywords)]

        # Join filtered elements into result_text
        result_text = "\n".join(result_list)

        # Update website_content_relevant dictionary
        website_content_relevant[url] = result_text

    # Remove entries with empty content
    website_content_relevant = {key: value for key, value in website_content_relevant.items() if value != ""}
    return website_content_relevant

