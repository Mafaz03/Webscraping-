# Set your OpenAI API key
# api_key = input("Enter api key: ")
import openai
from openai import OpenAI
import api_keys
from preprocess import get_valid_api_key

openai_api_list = api_keys.open_ai_key_list
api_key = get_valid_api_key(openai_api_list, for_which="OpenAI")
print("Openai api established")

client = OpenAI(api_key = api_key)

openai.api_key = api_key


def get_completion2(prompt, model = "gpt-3.5-turbo-1106"):
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    temperature = 0.7,
    messages=[
        {"role": "system", "content": "You are news reporter"},
        {"role": "user", "content": f"{prompt}"}
        ]
    )

    return completion.choices[0].message.content



def split_dict(dictionary, n_parts):
    # Calculate the number of items in each part
    items_per_part = len(dictionary) // n_parts
    
    # Split the dictionary keys and values into sub-lists
    keys_split = [list(dictionary.keys())[i:i + items_per_part] for i in range(0, len(dictionary), items_per_part)]
    values_split = [list(dictionary.values())[i:i + items_per_part] for i in range(0, len(dictionary), items_per_part)]
    
    # Create sub-dictionaries
    sub_dicts = [{k: v for k, v in zip(keys, values)} for keys, values in zip(keys_split, values_split)]
    
    return sub_dicts
