# Set your OpenAI API key
import openai
from openai import OpenAI


api_key = ""  # Enter your OpenAI API key here

client = OpenAI(api_key = api_key)
openai.api_key = api_key

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


