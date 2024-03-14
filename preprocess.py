import serpapi
from bs4 import BeautifulSoup
import pandas as pd
import cohere
from openai import OpenAI
import re
import tempfile
import textract
from docx import Document

from flask import Flask, render_template, request

from serpapi import GoogleSearch

from PyPDF2 import PdfReader
import os

def chunks(L, n): return [L[x: x+n] for x in range(0, len(L), n)]

def extract_text(file, file_extension):
    text = ""
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    file.save(temp_file_path)
    # import pdb;pdb.set_trace()
    if file_extension == 'pdf':
        # Extract text and decode bytes into a string
        text_bytes = textract.process(temp_file_path)
        text += text_bytes.decode('utf-8')  # Assuming UTF-8 encoding
    elif file_extension == 'csv':
        text += "="*20 + pd.read_csv(temp_file_path).to_string()
    elif file_extension == 'xlsx':
        text += "="*20 + pd.DataFrame(pd.read_excel(temp_file_path)).to_string()
    elif file_extension == "docx":
        doc = Document(temp_file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    elif file_extension == 'txt':
        with open(temp_file_path, 'r', encoding='utf-8') as txt_file:
            text += txt_file.read()
    
    os.remove(temp_file_path)  # Remove the temporary file
    return text

def make_links_clickable(text):
    # Regular expression to find URLs in the text
    url_pattern = re.compile(r'https?://\S+')
    
    def replace_link(match):
        url = match.group(0)
        return f'<a href="{url}" target="_blank" style="color: white; text-decoration: none; border-bottom: 1px solid white;">{url}</a>'
    
    # Replace URLs with HTML anchor tags
    return url_pattern.sub(replace_link, text)



def split_and_duplicate_keys(dictionary, max_chunk_size):
    """
    Splits the values of a given dictionary into chunks of a specified size and duplicates the keys.
    
    Parameters:
    -----------
    - dictionary (dict): The input dictionary where keys are strings and values are strings to be split.
    - max_chunk_size (int): The maximum size for each chunk of the string values.

    Returns:
    -----------
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
    -----------
    - input_dict (dict): The input dictionary.

    Returns:
    -----------
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


def is_valid_api_key(api_key, for_which):
    """
    Check if the provided API key is valid for the specified service.

    Parameters:
    -----------
        api_key (str): The API key to validate.
        for_which (str): The service for which the API key is being validated. 
            Should be either "Serp" or "OpenAI".

    Returns:
    -----------
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
            response = GoogleSearch(params)
            print("Serp Key passed")
            return True
        except:
            print("Serp Key failed")
            return False
        
    if for_which == "OpenAI":
        client = OpenAI(api_key = api_key)
        try:
            # Attempt to make a request to OpenAI's API
            completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are news assitant"},
                {"role": "user", "content": "Hello"}
                ]
            )
            # If successful, return True
            return True
        except:
            # If the error status indicates an invalid API key, return False
            return False


def get_valid_api_key(api_keys, for_which):
    """
    Iterate over a list of API keys and return the first valid one found for the specified service.

    Parameters:
    -----------
        api_keys (list of str): List of API keys to validate.
        for_which (str): The service for which the API key is being validated. 
            Should be either "Serp" or "OpenAI".

    Returns:
    -----------
        str or None: The first valid API key found, or None if no valid key is found.
    """
    if for_which == "Serp":
        for api_key in api_keys:
            # Check if the API key is valid
            if is_valid_api_key(api_key, for_which="Serp") == True:
                # If valid, return the current key
                return api_key
        # If no valid key is found, return None
        return None
    
    if for_which == "OpenAI":
        for api_key in api_keys:
            # Check if the API key is valid
            if is_valid_api_key(api_key, for_which="OpenAI"):
                # If valid, return the current key
                return api_key
        # If no valid key is found, return None
        return None

def clean_and_extract(text):
    soup = BeautifulSoup(text, 'html.parser')

    # Remove unwanted elements
    for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'iframe']):
        element.extract()

    # Extract main content
    main_content = soup.get_text(separator='\n', strip=True)

    return main_content



def rerank_df(df: pd.DataFrame, col_to_rank, col_to_address, query, api_key ,model = "rerank-english-v2.0", pprint = True):
    """
    Reranks a DataFrame based on a query using a specified model.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing documents to be reranked.
    col_to_rank : str
        Column name in DataFrame containing the text/documents to be ranked.
    col_to_address : str
        Column name in DataFrame containing the address of documents (for display).
    query : str
        Query string for reranking documents.
    model : str, optional
        Name of the reranking model to use, defaults to "rerank-english-v2.0".
    pprint : bool, optional
        If True, prints the document rank, index, document content, and relevance score, defaults to True.

    Returns:
    --------
    pd.DataFrame
        Reranked DataFrame with an additional "Relevance_Score" column, sorted by relevance score in descending order.
    """
    co = cohere.Client(api_key)
    Relevance_Score = []  # List to store relevance scores
    results = co.rerank(query=query, documents=list(df[col_to_rank]), model=model)  # Rerank documents
    for idx, r in enumerate(results):
        if pprint:  # If pprint is True, print document details
            print(f"Document Rank: {idx + 1}, Document Index: {r.index}")
            print(f"Document: {list(df[col_to_address])[r.index]}")
            print(f"Relevance Score: {r.relevance_score:.2f}")
        Relevance_Score.append(r.relevance_score)  # Append relevance score

    df["Relevance_Score"] = Relevance_Score  # Add relevance scores to DataFrame
    return df.sort_values(by="Relevance_Score", ascending=False)  # Sort DataFrame by relevance score


def get_raw_text(file_dir, file_paths):
    """
    Extracts raw text from PDF and text files.

    Args:
        file_paths (list): List of file paths to extract text from.

    Returns:
        str: Concatenated raw text extracted from all specified files.
    """
    raw_text = ""
    for file_path in file_paths:
        if os.path.exists(file_dir + "/" + file_path) :  # Check if the file path exists
            if file_path.endswith(".pdf"):
                try:
                    pdf_reader = PdfReader(file_dir + '/' + file_path)
                    for i, page in enumerate(pdf_reader.pages):
                        content = page.extract_text()
                        if content:
                            raw_text += content
                except Exception as e:
                    print(f"Error reading PDF file '{file_dir + '/' + file_path}': {e}")
            elif file_path.endswith(".txt"):
                try:
                    with open(file_dir + '/' + file_path, "r") as f:
                        raw_text += f.read()
                except Exception as e:
                    print(f"Error reading text file '{file_dir + '/' + file_path}': {e}")
            else:
                print(f"Unsupported file type: '{file_path}'")
        else:
            print(f"File not found: '{file_dir + '/' + file_path}'")
    return raw_text