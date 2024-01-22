# Set your OpenAI API key
api_key = ""  # Enter your OpenAI API key here

# Initialize the OpenAI API client
openai.api_key = api_key

def get_completion2(prompt, model="gpt-3.5-turbo-1106"):
    """
    Generates a completion for a given prompt using the OpenAI Chat API.

    Parameters:
    - prompt (str): The user's input prompt.
    - model (str): The OpenAI language model to use (default: "gpt-3.5-turbo-1106").

    Returns:
    - str: The generated completion for the prompt.
    """
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are news reporter"},
            {"role": "user", "content": f"{prompt}"}
        ]
    )
    return completion.choices[0].message.content

def split_dict(dictionary, n_parts):
    """
    Splits a dictionary into a specified number of sub-dictionaries.

    Parameters:
    - dictionary (dict): The original dictionary to be split.
    - n_parts (int): The number of parts to split the dictionary into.

    Returns:
    - list: A list of sub-dictionaries resulting from the split.
    """
    # Calculate the number of items in each part
    items_per_part = len(dictionary) // n_parts
    
    # Split the dictionary keys and values into sub-lists
    keys_split = [list(dictionary.keys())[i:i + items_per_part] for i in range(0, len(dictionary), items_per_part)]
    values_split = [list(dictionary.values())[i:i + items_per_part] for i in range(0, len(dictionary), items_per_part)]
    
    # Create sub-dictionaries
    sub_dicts = [{k: v for k, v in zip(keys, values)} for keys, values in zip(keys_split, values_split)]
    
    return sub_dicts
