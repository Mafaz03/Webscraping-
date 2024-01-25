from tqdm import tqdm

def keyword_extractor_paragraph(website_content: dict[str, str], keywords: list, filter_by_amount: int = None):
    """
    Extracts only those paragraphs that have a keyword in it and length above 60.

    Args:
    website_content (dictionary): URL and website's HTML content.
    keywords (list): List of keywords to search for.
    filter_by_amount (int): if the html content is more than this, only then keep the content.

    Returns:
    website_content_relevant (dictionary): URL and website's keyword-extracted HTML content.
    """
    website_content_relevant = {}

    for url, text in tqdm(website_content.items()):
        list_of_split = text.split('\n')
        non_empty_list = [element for element in list_of_split if element != ""]

        # Use result_list in the condition for the second list comprehension
        if filter_by_amount != None:
            result_list = [element for element in non_empty_list if any(keyword.lower() in element.lower() for keyword in keywords) and len(element) > 60]
        else:
            result_list = [element for element in non_empty_list if any(keyword.lower() in element.lower() for keyword in keywords)]

        # Join result_list instead of non_empty_list
        result_text = "\n".join(result_list)

        
        website_content_relevant[url] = result_text

    website_content_relevant = {key: value for key, value in website_content_relevant.items() if value != ""}
    return website_content_relevant
