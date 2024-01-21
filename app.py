# Importing necessary dependencies
from time import time
app_start_time = time()

from flask import Flask, render_template, request, jsonify, redirect
import html
from urllib.parse import quote
from htmldate import find_date
from datetime import datetime
from tqdm import tqdm
import pandas as pd

# Importing custom modules
from html_extractor import *
from get_suburls import *
from openai_func import *
from get_date import *
from mongo_utils import import_from_mongo, save_to_mongo
from url_stats import plot_date
from search_results import *

import matplotlib
matplotlib.use('agg')

from keyword_extraction import keyword_extractor_paragraph as kep

from pymongo import MongoClient
import certifi
ca = certifi.where()

# Setting up Flask app
app = Flask(__name__)

# Flask route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route for handling scraping request
@app.route('/scrape', methods=['POST'])
def scrape():
    print("""
         ____                    ____                                 
        |  _ \  ___  ___ _ __   / ___|  ___ _ __ __ _ _ __   ___ _ __ 
        | | | |/ _ \/ _ | '_ \  \___ \ / __| '__/ _` | '_ \ / _ | '__|
        | |_| |  __|  __| |_) |  ___) | (__| | | (_| | |_) |  __| |   
        |____/ \___|\___| .__/  |____/ \___|_|  \__,_| .__/ \___|_|   
                        |_|                          |_|                
        """)
        
    # Extracting data from the JSON request
    data = request.get_json()
    print("Received Data:", data)
    url = data.get('urls')
    keyword = data.get('keyword')
    prompt = data.get('prompt')

    # Printing relevant information
    print(f"Scraping URL: {url}")
    print(f"Searching for keyword: {keyword}")
    print(f"Prompt is: {prompt}")

    # Setting up excluded domains and search extras
    excluded_domains = r'(magicbricks|play\.google|facebook\.com|twitter\.com|instagram\.com|linkedin\.com|youtube\.com|\.gov|\.org|policy|terms|buy|horoscope|web\.whatsapp\.com|\.(png|jpg|jpeg|gif|bmp|tiff|webp|443))'
    search_extras = ["?s=", "/search/", "/search?q=", "/topic/"]
    
    # Generating search result URLs
    search_result_url = generate_urls_with_exclusions(base_urls=url, search_extras=search_extras, keywords=keyword.split(','), excluded_domains=excluded_domains)
    search_result_url = list(search_result_url)

    if len(search_result_url) >= 0:
        print("\n".join(search_result_url[:5]))

    # Scraping sub-URLs for detailed information
    scraper = WebScraper2(sub_url_size=1, keywords=keyword)
    urls_list_str = ",".join(search_result_url)
    inside_urls1, failed_fetch1, sub_url_size1, total_size1 = scraper.get_suburls2(urls_list_str)
    print("Failed Fetch:", failed_fetch1)
    print("Splits:", len(inside_urls1))
    print("Tree size:", total_size1)

    # Extracting sub-URLs
    scraper = WebScraper2(sub_url_size=3, keywords=keyword)
    urls_list_str = ",".join(url)
    inside_urls, failed_fetch, sub_url_size, total_size = scraper.get_suburls2(urls_list_str)
    print("Failed Fetch:", failed_fetch)
    print("Splits:", len(inside_urls))
    print("Tree size:", total_size)

    # Handling cases when there's nothing to display
    if len(url) - total_size == 0:
        response_complete = "There was nothing to display\n\nKeywords didn't match any URLs\nPlease add additional URLs"
    else:
        # Joining sub-URLs into a single list
        website_urls = [item for sublist in list(inside_urls.values()) for item in sublist]
        website_urls1 = [item for sublist in list(inside_urls1.values()) for item in sublist]
        website_urls = website_urls1 + website_urls

        # Importing Date database from MongoDB
        date_db_name = "PetraOil"
        collection_db_name = "Date Database"
        columns = ["url", "Date"]
        mongo_date_df = import_from_mongo(date_db_name, collection_db_name, columns)

        print(f"date_db_name: {date_db_name}")
        print(f"collection_db_name: {collection_db_name}")
        print("Imported Successful")

        # Creating a DataFrame of extracted URLs
        urls_from_extraction = pd.DataFrame(website_urls[:])
        urls_from_extraction.columns = ["url"]

        # Identifying URLs not yet indexed in the database
        df_of_which_to_find_the_date_of = pd.merge(mongo_date_df, urls_from_extraction, how="outer")
        df_of_which_to_find_the_date_of = df_of_which_to_find_the_date_of.loc[
            ~df_of_which_to_find_the_date_of['Date'].notna(), :]
        df_of_which_to_find_the_date_of = df_of_which_to_find_the_date_of.drop_duplicates(subset='url', keep='first')

        print(f"Dates yet to index: {df_of_which_to_find_the_date_of.shape[0]}")

        list_of_which_to_find_the_date_of = list(df_of_which_to_find_the_date_of["url"].values)

        # Getting dates for extracted URLs that aren't indexed in the database
        url_date_list = []
        timeout_seconds = 5

        for url in tqdm(list_of_which_to_find_the_date_of):
            start_time = time()
            try:
                # Your function to fetch the date from the URL
                date_value = fetch_date_from_url(url)
            except Exception as e:
                # Handle exceptions, e.g., print an error message or store a default value
                print(f"Error fetching date for {url}: {e}")
                date_value = None

            elapsed_time = time() - start_time

            # Append to the list if the operation took less than the timeout
            if elapsed_time < timeout_seconds:
                url_date_list.append([url, date_value])
            else:
                print(f"Skipping {url} due to timeout of {timeout_seconds}s")

        url_date_dict = {i[0]: i[1] for i in url_date_list}

        # Insert the document into the collection
        data = url_date_dict
        save_to_mongo(date_db_name, collection_db_name, data=data)

        urls_date_df = pd.merge(urls_from_extraction, mongo_date_df, on='url', how='inner').sort_values(by="Date",
                                                                                                       ascending=False)

        # Columns
        print(urls_date_df.columns)
        plot_date(urls_date_df, save_path=f"Plots/{datetime.now()}.jpg")

        # S = " Filtering by date "
        print("\n\n" + " Filtering by date ".center(100, '=') + "\n")

                # Setting up start and end dates for filtering URLs
        start_date = pd.to_datetime('14-09-2022', format='%d-%m-%Y')
        end_date = pd.to_datetime('01-11-2024', format='%d-%m-%Y')

        # Filtering URLs based on the date range
        df_filtered_by_date = urls_date_df[(urls_date_df["Date"] >= start_date) & (urls_date_df["Date"] <= end_date)]

        # Displaying the number of URLs within the specified date range
        print(f"Amount of URLs between the dates: {df_filtered_by_date.shape[0]}")

        # Checking if there are URLs within the date range
        if df_filtered_by_date.shape[0] > 0:
            # Setting up database names and columns for HTML extraction
            date_db_name = "PetraOil"
            collection_db_name = "Html Database"
            columns = ["url", "Html"]

            # Importing HTML data from MongoDB
            mongo_html_df = import_from_mongo(date_db_name, collection_db_name, columns)

            # Merging HTML DataFrame with URLs to find which HTMLs are yet to be indexed
            df_of_which_to_find_the_html_of = pd.merge(mongo_html_df, pd.DataFrame(df_filtered_by_date["url"]),
                                                       how="outer")
            df_of_which_to_find_the_html_of = df_of_which_to_find_the_html_of.loc[
                ~df_of_which_to_find_the_html_of['Html'].notna(), :]
            df_of_which_to_find_the_html_of = df_of_which_to_find_the_html_of.drop_duplicates(subset='url',
                                                                                                keep='first')

            print(f"HTML yet to index: {df_of_which_to_find_the_html_of.shape[0]}")

            # Extracting URLs for which HTML needs to be obtained
            list_of_which_to_find_the_html_of = list(df_of_which_to_find_the_html_of["url"])
            url_html_extracted, _ = get_html(list_of_which_to_find_the_html_of)

            # Saving the extracted HTML data to MongoDB
            data = url_date_dict
            date_db_name = "PetraOil"
            collection_db_name = "Html Database"
            save_to_mongo(date_db_name, collection_db_name, data=url_html_extracted)
            columns = ["url", "Html"]
            mongo_html_df = import_from_mongo(date_db_name, collection_db_name, columns)

            # Displaying message for HTML extraction process
            S = " Getting HTML content for particular URLs "
            print("\n\n" + S.center(100, '=') + "\n")

            # Sorting HTML DataFrame based on dates and selecting a subset for processing
            url_html_df_date_sorted = mongo_html_df[mongo_html_df['url'].isin(list(df_filtered_by_date["url"]))]

            page = 1
            amount_of_content = 20
            url_html_df_date_sorted_10 = url_html_df_date_sorted[
                (page - 1) * amount_of_content: amount_of_content * page]  # Only 10 at a time

            # Creating a dictionary for URL and corresponding HTML
            url_html_dict = url_html_df_date_sorted_10.set_index('url')['Html'].to_dict()

            try:
                del url_html_extracted["_id"]
                print("Deleted _id")
            except:
                pass

            # Extracting content using OpenAI API
            url_extracted_html = kep(website_content=url_html_dict, keywords=keyword, filter_by_amount=60)

            # Creating a list of tuples containing URL and a portion of the extracted HTML
            content_list = [(key, value[:2000]) for key, value in url_extracted_html.items()]

            MAX_CONTENT = 5

            content_list_complete = []

            iterations = len(content_list) // MAX_CONTENT

            # Splitting the content into batches
            for i in range(iterations):
                sub_content_list = content_list[MAX_CONTENT * i: MAX_CONTENT * (i + 1)]
                content_list_complete.append(sub_content_list)

            # Handling remaining elements after the loop
            remaining_elements = content_list[MAX_CONTENT * iterations:]
            if remaining_elements:
                iterations += 1
                content_list_complete.append(remaining_elements)

            # Displaying message for OpenAI API execution
            S = " OpenAI's API execution "
            print("\n\n" + S.center(100, '=') + "\n")

            # Setting up the question for OpenAI API
            question = prompt
            print(f"Iterations: {iterations}")
            response_complete = ''

            # Looping through batches and fetching responses from OpenAI API
            for data_idx in tqdm(range(iterations)):
                prompt = f"""
                    Data is in the form of tuples inside list: {content_list_complete[data_idx]} \n\n\n 
                    Question: {question} \n\n\n
                    Method of reply: 100 - 200 word sentences, clear reply,
                    provide URL if necessary.
                    """

                # Adding a sleep to avoid API rate limits
                if data_idx + 1 % 6 == 0:
                    sleep(20)

                # Fetching response from OpenAI API
                response = get_completion2(prompt)
                response_complete += response + "\n\n"
                print(f"Batch {data_idx + 1} out of {iterations} completed ")

        else:
            response_complete = "There was nothing to display\n\nURLs don't exist within the particular time frame\nPlease try expanding the time frame and try again"

        # Printing the completion time
        app_end_time = time()
        print(f"Completed in {app_end_time - app_start_time:.2f}s")

    # Dummy response for demonstration purposes
    response_data = {"url": url}

    # Stripping extra whitespaces from the response
    response_complete = response_complete.strip()

    # Redirecting to the result page with the formatted response
    response_complete = response_complete.replace('\n', '<br>')
    return redirect('/result?response_complete=' + response_complete)

# Flask route for displaying the result page
@app.route('/result')
def result():
    response_complete = request.args.get('response_complete', '')
    return render_template('result.html', result_data=response_complete)

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
