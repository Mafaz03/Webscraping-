import serpapi
from bs4 import BeautifulSoup

def split_and_duplicate_keys(dictionary, max_chunk_size):
    """
    Splits the values of a given dictionary into chunks of a specified size and duplicates the keys.
    
    Parameters:
    - dictionary (dict): The input dictionary where keys are strings and values are strings to be split.
    - max_chunk_size (int): The maximum size for each chunk of the string values.

    Returns:
    dict: A new dictionary with duplicated keys and split values. The original values in the input
          dictionary remain unchanged. The keys for the split values include the original key for
          the first chunk, and additional keys with a suffix ' part_' and the chunk index for the
          subsequent chunks.
    """
    new_dict = {}

    for key, value in dictionary.items():
        chunks = [value[i:i + max_chunk_size] for i in range(0, len(value), max_chunk_size)]
        
        # Duplicate the key for each chunk (excluding the first chunk)
        keys = [key] + [key + f' part_{i + 1}' for i in range(len(chunks) - 1)]
        
        # Assign each key its corresponding chunk
        new_dict.update({k: v for k, v in zip(keys, chunks)})

    return new_dict


def keep_first_occurrence(input_dict):
    """
    Filter a dictionary to keep only the first occurrence of each unique value.

    Parameters:
    - input_dict (dict): The input dictionary.

    Returns:
    - dict: A new dictionary containing only the first occurrence of each unique value.
    """
    seen_values = set()
    filtered_dict = {}

    for key, value in input_dict.items():
        if value not in seen_values:
            seen_values.add(value)
            filtered_dict[key] = value

    return filtered_dict    



def prepend_dict(original_dict, new_dict): return {**new_dict, **original_dict}


def is_valid_api_key(api_key: str, for_which: str):
    """
    Check if the provided API key is valid for the specified service.

    Parameters:
        api_key (str): The API key to validate.
        for_which (str): The service for which the API key is being validated. 
            Should be either "Serp" or "OpenAI".

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    if for_which == "Serp":
        # Define parameters for a minimal search request
        params = {
            "q": "cat",
            "api_key": api_key,
            "num": 1
        }
        try:
            # Attempt to make a minimal search request
            response = serpapi.search(params)
            # If successful, return True
            return True
        except serpapi.exceptions.SerpApiError as e:
            # If the error status indicates an invalid API key, return False
            return False
        
    if for_which == "OpenAI":
        pass


def get_valid_api_key(api_keys: list, for_which: str):
    """
    Iterate over a list of API keys and return the first valid one found for the specified service.

    Parameters:
        api_keys (list of str): List of API keys to validate.
        for_which (str): The service for which the API key is being validated. 
            Should be either "Serp" or "OpenAI".

    Returns:
        str or None: The first valid API key found, or None if no valid key is found.
    """
    if for_which == "Serp":
        for api_key in api_keys:
            # Check if the API key is valid
            if is_valid_api_key(api_key, for_which="Serp"):
                # If valid, return the current key
                return api_key
        # If no valid key is found, return None
        return None
    
    if for_which == "OpenAI":
        pass

def clean_and_extract(text):
    soup = BeautifulSoup(text, 'html.parser')

    # Remove unwanted elements
    for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'iframe']):
        element.extract()

    # Extract main content
    main_content = soup.get_text(separator='\n', strip=True)

    return main_content