# app.py


## Importing Dependencies
from time import time
app_start_time = time()

from flask import Flask, render_template, request, jsonify,redirect, url_for,escape
import html
from urllib.parse import quote
import requests
from htmldate import find_date
from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup
import ssl
from tqdm import tqdm
from textblob import TextBlob
import openai
import multiprocessing
import pandas as pd
import numpy as np 
from time import sleep

from html_extractor import *
from get_suburls import *
from openai_func import *
from get_date import *
# from parallel import *
from mongo_utils import import_from_mongo, save_to_mongo
from url_stats import plot_date
from search_results import *
from preprocess import *
import api_keys
import matplotlib
matplotlib.use('agg')

import serpapi

from keyword_extraction import keyword_extractor_paragraph as kep


from pymongo import MongoClient
import certifi
ca = certifi.where()



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
        
    data = request.get_json()
    print("Received Data:",data)
    url = data.get('urls')
    keyword = data.get('keyword')
    prompt=data.get('prompt')

    keyword_list = [i.strip() for i in keyword.split(",")]

    from_date_str = data.get('from_date')
    to_date_str = data.get('to_date')


    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').strftime('%d-%m-%Y')
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').strftime('%d-%m-%Y')

    print("From",from_date)
    print("to",to_date)

    # Replace the following print statements with your actual scraping logic
    print(f"Scraping URL: {url}")
    print(f"Senching for keyword: {keyword}")
    print(f"prompt is: {prompt}")

    SEARCH_BAR_SCRAPE = 1
    GENERAL_DEEP_SCRAPE = 1 
    ADVANCED_SEARCH = 1

    inside_urls1 = []
    inside_urls2 = []
    inside_urls3 = []

    website_urls1 = []
    website_urls2 = []
    website_urls3 = []

    if SEARCH_BAR_SCRAPE == 1:
        S = " Search Bar Scrape "
        print("\n\n"+S.center(100, '=')+"\n")
        base_urls = url

        search_extras = ["?s=", "/search/", "/search?q=", "/topic/"]
        keywords_list = keyword.split(',')
        excluded_domains = r'(magicbricks|443|play\.google|facebook\.com|twitter\.com|instagram\.com|linkedin\.com|youtube\.com|\.gov|\.org|policy|terms|buy|horoscope|web\.whatsapp\.com|\.(png|jpg|jpeg|gif|bmp|tiff|webp))'
        result_urls = generate_urls_with_exclusions(base_urls, search_extras, keywords_list, excluded_domains)
        print('\n'.join(result_urls))

        search_html = get_html(list(result_urls), mode_of_search="Search Bar Scrape")
        print(f"Failed to get html: {search_html[1]}")
        search_html_content = search_html[0]

        base_url_html_content = get_html(urls=base_urls)[0]
        search_html = prepend_dict(search_html_content, base_url_html_content)
        search_html_pruned = keep_first_occurrence(search_html)

        print("Pruning Completed", len(search_html) - len(search_html_pruned), "Deleted")
    
        urls_list = list(search_html_pruned.keys())
        urls_list_str = ",".join(urls_list)

        scraper = WebScraper2(sub_url_size=1 , keywords=keyword)
        inside_urls, failed_fetch, sub_url_size, total_size = scraper.get_suburls2(urls_list_str)

        # print("Inside URLs:", inside_urls)
        print("Failed Fetch:", failed_fetch)
        print("Splits:", len(inside_urls))
        print("Tree size:", total_size)

        ## Joining sub urls into one single list
        website_urls1 = inside_urls[1]
        
        print("\n".join(website_urls1[:10]))

    if GENERAL_DEEP_SCRAPE == 1:

        S = " General Deep Scrape "
        print("\n\n"+S.center(100, '=')+"\n")

        ## Extracting sub urls
        urls_list_str = ",".join(url)
        scraper = WebScraper2(sub_url_size = 3 , keywords = keyword)
                    
        inside_urls2, failed_fetch, sub_url_size, total_size2 = scraper.get_suburls2(urls_list_str)
        # print("Inside URLs:", inside_urls)
        print("Failed Fetch:", failed_fetch)
        print("Splits:", len(inside_urls2))
        print("Tree size:", total_size2)

        ## Joining sub urls into one single list
        website_urls2 = [item for sublist in list(inside_urls2.values()) for item in sublist]
        print("\n".join(website_urls2[3:13]))
        
    if ADVANCED_SEARCH == 1:

        S = " Advanced Search "
        print("\n\n"+S.center(100, '=')+"\n")
        
        Serp_api_list = api_keys.serp_key_list
        Serp_api = get_valid_api_key(Serp_api_list, for_which="Serp")

        for ad_url in tqdm(url):

            params = {
            "q": f"{' '.join(keyword_list)} site:{ad_url}",
            "google_domain": "google.com",
            "api_key": Serp_api,
            "num": 50,
            "tbs": f"cdr:1,cd_min:{from_date.replace('-', '/')},cd_max:{to_date.replace('-', '/')}"
            }

            search = serpapi.search(params)
            link_results = [dict(search)["organic_results"][i]["link"] for i in range(len(dict(search)["organic_results"]))]
            website_urls3.append(link_results)

        website_urls3 = link_results
        print("\n".join(website_urls3[:10]))


    website_urls = website_urls1 + website_urls2 + website_urls3

    if len(website_urls) == 0:
        response_complete = "There was nothing to display\n\nKeywords did'nt match any urls\nPlease add additional urls"
       
    else:
        print("length of urls: ",len(website_urls))

        S = " Importing Database for Date "
        print("\n\n"+S.center(100, '=')+"\n")

        ## DB integration for Date
        ### Importing Date db from mongo
        date_db_name = "PetraOil"
        collection_db_name = "Date Database"
        columns = ["url", "Date"]
        mongo_date_df = import_from_mongo(date_db_name, collection_db_name, columns)

        print(f"date_db_name: {date_db_name}")
        print(f"collection_db_name: {collection_db_name}")
        print("Imported Successful")

        ### Urls of extracted sub urls
        urls_from_extraction = pd.DataFrame(website_urls[:]) 
        urls_from_extraction.columns = ["url"]

        ### Urls that arent yet indexed in db
        df_of_which_to_find_the_date_of = pd.merge(mongo_date_df, urls_from_extraction, how = "outer")
        df_of_which_to_find_the_date_of = df_of_which_to_find_the_date_of.loc[~df_of_which_to_find_the_date_of['Date'].notna(), :] # Dates that are yet found out
        df_of_which_to_find_the_date_of = df_of_which_to_find_the_date_of.drop_duplicates(subset='url', keep='first')              # Dropping duplicates if any


        S = " Getting Dates for "
        print("\n\n"+S.center(100, '=')+"\n")

        print(f"Dates yet to index: {df_of_which_to_find_the_date_of.shape[0]}")

        list_of_which_to_find_the_date_of = list(df_of_which_to_find_the_date_of["url"].values)

        ### Getting dates for extracted urls that arent indexed in DB
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

            
        url_date_dict = {i[0] : i[1] for i in url_date_list}
        

        # Insert the document into the collection

        S = " Indexing to Database "
        print("\n\n"+S.center(100, '=')+"\n")

        data = url_date_dict
        date_db_name = "PetraOil"
        collection_db_name = "Date Database"


        save_to_mongo(date_db_name, collection_db_name, data = data)

        urls_date_df = pd.merge(urls_from_extraction, mongo_date_df, on='url', how='inner').sort_values(by="Date",ascending=False)
        
        # Columns
        print(urls_date_df.columns)
        plot_date(urls_date_df, save_path=f"Plots/{datetime.now()}.jpg")

        # print(urls_date_df.isna().sum())

        S = " Filtering by date "
        print("\n\n"+S.center(100, '=')+"\n")

        start_date = pd.to_datetime(from_date,format='%d-%m-%Y')
        end_date = pd.to_datetime(to_date,format='%d-%m-%Y')

        df_filtered_by_date = urls_date_df[(urls_date_df["Date"] >= start_date) & (urls_date_df["Date"] <= end_date)]
        
        print(f"Amount of urls between the dates: {df_filtered_by_date.shape[0]}")

        if df_filtered_by_date.shape[0] >= 0:

            date_db_name = "PetraOil"
            collection_db_name = "Html Database"
            columns = ["url", "Html"]
            mongo_html_df = import_from_mongo(date_db_name, collection_db_name, columns)

            df_of_which_to_find_the_html_of = pd.merge(mongo_html_df, pd.DataFrame(df_filtered_by_date["url"]) , how = "outer")
            df_of_which_to_find_the_html_of = df_of_which_to_find_the_html_of.loc[~df_of_which_to_find_the_html_of['Html'].notna(), :] # Dates that are yet found out
            df_of_which_to_find_the_html_of = df_of_which_to_find_the_html_of.drop_duplicates(subset='url', keep='first')              # Dropping duplicates if any

            print(f"Html yet to index: {df_of_which_to_find_the_html_of.shape[0]}")

            list_of_which_to_find_the_html_of = list(df_of_which_to_find_the_html_of["url"])
            url_html_extracted,_ = get_html(list_of_which_to_find_the_html_of)
            data = url_date_dict
            date_db_name = "PetraOil"
            collection_db_name = "Html Database"
            save_to_mongo(date_db_name, collection_db_name, data = url_html_extracted)
            columns = ["url", "Html"]
            mongo_html_df = import_from_mongo(date_db_name, collection_db_name, columns)

            S = " Getting html content for particular urls "
            print("\n\n"+S.center(100, '=')+"\n")
            

            url_html_df_date_sorted = mongo_html_df[mongo_html_df['url'].isin(list(df_filtered_by_date["url"]))]


            page = 1
            amount_of_content = 20
            url_html_df_date_sorted_10 = url_html_df_date_sorted[(page - 1) * amount_of_content : amount_of_content * page]  # Only 10 at a time

            url_html_dict = url_html_df_date_sorted_10.set_index('url')['Html'].to_dict()
            url_html_dict = {key : clean_and_extract(value) for key,value in url_html_dict.items()}  # Cleaning the Text
            try:
                del url_html_extracted["_id"]
                print("Deleted _id")
            except:
                pass

            url_extracted_html = kep(website_content = url_html_dict, keywords = " ", filter_by_amount = 30)
            # url_extracted_html = url_html_dict

            url_html_content_txt = ''
            for key, val in url_extracted_html.items():
                url_html_content_txt += key + '\n\n' + val + '\n\n' + '-'*50 + '\n\n'

            with open(f"Output text/{datetime.now()}.txt", "w") as f:
                f.write(url_html_content_txt)

            content_list = [(key,value[:2000]) for key, value in url_extracted_html.items()] # 2000 is temporary until tokenier function is not set up

            MAX_CONTENT = 5

            content_list_complete = []

            iterations = len(content_list) // MAX_CONTENT


            for i in range(iterations):
                sub_content_list = content_list[MAX_CONTENT * i: MAX_CONTENT * (i + 1)]
                content_list_complete.append(sub_content_list)


            # Handle remaining elements after the loop
            remaining_elements = content_list[MAX_CONTENT * iterations:]
            if remaining_elements:
                iterations += 1
                content_list_complete.append(remaining_elements)

            S = " Openai's api execution "
            print("\n\n"+S.center(100, '=')+"\n")

            question = prompt
            print(f"Itterations: {iterations}")
            response_complete = ''
            for data_idx in tqdm(range(iterations)):

                prompt = f""" 
                    Data is in the form of tuples inside list: {content_list_complete[data_idx]} \n\n\n 
                    Question: {question} \n\n\n
                    Method of reply: 100 - 200 word sentences, clear reply,
                    provide url if neccessary.
                    """
                
                if data_idx +1 % 6 == 0:
                    sleep(20)

                response = get_completion2(prompt)
                response_complete += response + "\n\n"
                print(f"Batch {data_idx + 1} out of {iterations} completed ")

        else:
            response_complete = "There was nothing to display\n\nURLS dont exist within the particular Time frame\nPlease try expanding the time frame and try again"

        # print(response_complete)

    
    app_end_time = time()
    
    print(f"Completed in {app_end_time - app_start_time :.2f}s")




    # Dummy response for demonstration purposes
    response_data = {"url" : url}
    # trying to solve the bug....
    response_complete = response_complete.strip()
    # return jsonify({'result':response_complete})
    # url_encoded_response = quote(response_complete)
    # return redirect('/result?response_complete=' + response_complete)
    
    # return redirect('/result?response_complete=' + response_complete.replace('\n', ''))


    # print("Original response_complete:", response_complete)
    response_complete = response_complete.replace('\n', '<br>')
    # print("Transformed response_complete:", response_complete)
    return redirect('/result?response_complete=' + response_complete)

   
    # return redirect('/result?response_complete=' + response_complete.replace('\n', '<br>'))
    # print("Transformed response_complete:", response_complete)

    # return redirect(url_for('result', response_complete=response_complete))



@app.route('/result')
def result():
      response_complete = request.args.get('response_complete', '')
      
    #   print("The data this is what it got:",response_complete);
      return render_template('result.html', result_data=response_complete)






    #  response_complete = request.args.get('response_complete')
    #  response_complete_decoded = unquote(response_complete)
    #  escaped_text = escape(response_complete_decoded)

    #  print(f'decoddedBrooo: {response_complete_decoded}')
    #  print(f'escapedd {escaped_text}')
    #  return render_template('result.html', result_data=escaped_text),200,{'Content-Type': 'text/html'}




if __name__ == '__main__':
    app.run(debug=True)
