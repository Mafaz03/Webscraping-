# app.py

## Importing Dependencies
from time import time

import datetime as dt

def get_indian_date_time(): return dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30))).strftime("%dth %b %Y, %I:%M%p")
india_time = get_indian_date_time()

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
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
import openai
import pandas as pd
import numpy as np 
from time import sleep
from datetime import date

from serpapi import GoogleSearch

from html_extractor import *
from deletion_helper import *
from get_suburls import *
from openai_func import *
from get_date import *
from mongo_utils import import_from_mongo, save_to_mongo
from url_stats import plot_date
from search_results import *
from preprocess import *
from plotting_func import *
import api_keys
import matplotlib
matplotlib.use('agg')
from markupsafe import Markup, escape

import openai_func
import os

import serpapi
import cohere

from flask_socketio import SocketIO,emit

from keyword_extraction import keyword_extractor_paragraph as kep

from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import OpenAI

import smtplib
import ssl
import certifi

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

from email_helper import *

port = 587  # For starttls
smtp_server = "smtp.gmail.com"
sender_email = "bat463660@gmail.com"
dev_emal = "mohdmafaz200303@gmail.com"
receiver_email = "petraoil.prod@gmail.com"
sender_password = "bygc aape tnem adev"


import tempfile

from flask_cors import CORS
import json

from progress import *


from pymongo import MongoClient
import certifi
ca = certifi.where()




app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

app.secret_key = 'petraoilscraperproject'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chatbot')
def chat_bot():
    return render_template('home.html')


@app.route("/get")
def get_bot_response():
    global conversation_context

    query = request.args.get('msg')

    # If it's a follow-up question, use the previous documents
    if conversation_context["last_question"] and conversation_context["docs"]:
        docs = conversation_context["docs"]
    else:
        # Otherwise, perform a new search
        docs = document_search.similarity_search(query)

    ans = chain.run(input_documents=docs, question=query)

    # Update conversation context
    conversation_context["docs"] = docs
    conversation_context["last_question"] = query

    return ans

os.environ["OPENAI_API_KEY"] = openai_func.api_key

@app.route('/process_files',methods=['POST'])
def process_files():
       global document_search
       global chain
       global conversation_context

       try:           

        
        # file_contents = [file.filename for file in request.files.getlist('files')]
        files = request.files.getlist('files[]')
        print(files)
        if not files:
            return "No files uploaded"

        texts = []
        for file in files:
            filename = file.filename
            if filename == '':
                continue

            file_extension = filename.rsplit('.', 1)[1].lower()
            if file_extension in ['pdf', 'txt']:
                text = extract_text(file, file_extension)
                texts.append((filename, text))
            else:
                 return jsonify({'error': f'Unsupported file format: {filename}'})

        raw_text = ''.join(text)
        # raw_text = get_raw_text("Output text", file_contents)

        # Split text using Character Text Split
        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1000, chunk_overlap=600, length_function=len
        )
        texts = text_splitter.split_text(raw_text)

        # Download embeddings from OpenAI
        embeddings = OpenAIEmbeddings()

        # Create FAISS vector store from texts
        document_search = FAISS.from_texts(texts, embeddings)

        # Load question-answering chain
        chain = load_qa_chain(OpenAI(), chain_type="stuff")

        # Initialize conversation context
        conversation_context = {"docs": None, "last_question": None}
        print("YESS")
        return jsonify({'success': True, 'message': 'File data received and processed successfully'})
       
       except Exception as e:
            print(f"Error: {e}")
            
            return jsonify({'error': str(e)}), 500

@app.route('/scrape', methods=['POST'])
def scrape():
    app_start_time = time()

    # Deletion
    directory_path = "Output text"
    delete_files_until_limit(directory_path, limit = 20)

    # Deletion
    directory_path = "Output text"
    delete_files_until_limit(directory_path, limit = 20)

    directory_path = "Plots"
    delete_files_until_limit(directory_path, limit = 20)

    socketio.emit('print_output', {'output': f'Caches Cleared'})

    log_str = ""
    scrape_start_time = time()

    print("""
         ____                    ____                                 
        |  _ \  ___  ___ _ __   / ___|  ___ _ __ __ _ _ __   ___ _ __ 
        | | | |/ _ \/ _ | '_ \  \___ \ / __| '__/ _` | '_ \ / _ | '__|
        | |_| |  __|  __| |_) |  ___) | (__| | | (_| | |_) |  __| |   
        |____/ \___|\___| .__/  |____/ \___|_|  \__,_| .__/ \___|_|   
                        |_|                          |_|                
        """)
        
    sources_str = 'failed to fetch'
    
    data = request.get_json()
    print("Received Data:",data)
    # socketio.emit('print_output', {'output': 'Received Data: ' + json.dumps(data)})

    S = progress_bar_once(" Received Data ", title=True, num = 100)
    socketio.emit('print_output', {'output': S})
    
    socketio.emit('print_output', {'output': 'Urls Recieved: ' + json.dumps(data["urls"])})
    socketio.emit('print_output', {'output': 'Keywords Recieved: ' + json.dumps(data["keyword"])})
    socketio.emit('print_output', {'output': 'Prompt Recieved: ' + json.dumps(data["prompt"])})
    if data["to_date"] == "":
        socketio.emit('print_output', {'output': 'If `From Date` or `To Date` are absent, algorithm will set it to be from `today` to `2 years back`'})


    url = data.get('urls')
    keyword = data.get('keyword')
    prompt=data.get('prompt')

    log_str += "urls:\n".join(url)
    log_str += f"\nKeywords: {keyword}"
    log_str += f"\nPrompt: {prompt}"
    

    keyword_list = [i.strip() for i in keyword.split(",")]

    from_date_str = data.get('from_date')
    to_date_str = data.get('to_date')


    today = date.today()
    if to_date_str == '':
        to_date_str = str(today)
        log_str += "\nto date not entered\n"

    if from_date_str == '':
        from_date_str = str(today.year - 2) + '-' + str(today.month) + '-' +str(today.day)
        log_str += "from date not entered"

    socketio.emit('print_output', {'output': 'From Date Recieved: ' + json.dumps(from_date_str)})
    socketio.emit('print_output', {'output': 'To Date Recieved: ' + json.dumps(to_date_str)})

    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').strftime('%d-%m-%Y')
    from_date_modified = from_date
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').strftime('%d-%m-%Y')

    log_str += f"\nFrom date: {from_date_str}\nTo date: {to_date_str}\n\n"

    log_str += "#"*20

    selectedOptions = data.get('selectedOption', [])

    S = progress_bar_once(" Selected Options ", title=True, num = 100)
    socketio.emit('print_output', {'output': S})

    print("The option choosen is",selectedOptions) 
    print("From",from_date)
    print("to",to_date)

    # Replace the following print statements with your actual scraping logic
    print(f"Scraping URL: {url}")
    print(f"Senching for keyword: {keyword}")
    print(f"prompt is: {prompt}")

# display the progress..
    # socketio.emit('print_output',{'type':'ChoosenOptions', 'output':"Scraping URL: " + json.dumps(url)})
    # socketio.emit('print_output',{'type':'ChoosenOptions', 'output':"Searching for keyword: " + json.dumps(keyword)})
    # socketio.emit('print_output',{'type':'ChoosenOptions', 'output':"prompt is: " + json.dumps(prompt)})

    SORT_BY_RELAVANCY = 1

    SEARCH_BAR_SCRAPE = 0
    GENERAL_DEEP_SCRAPE = 0
    ADVANCED_SEARCH = 0

    

    if len(selectedOptions) != 0:
        for choice in selectedOptions:
            if choice == "search-bar":
                SEARCH_BAR_SCRAPE = 1
                socketio.emit('print_output',{'type':'ChoosenOptions', 'output': "The option chosen is SEARCH_BAR_SCRAPE"})
            if choice == "general-deep":
                GENERAL_DEEP_SCRAPE = 1
                socketio.emit('print_output',{'type':'ChoosenOptions', 'output': "The option chosen is GENERAL_DEEP_SCRAPE"})
            if choice == "advance":
                ADVANCED_SEARCH = 1
                socketio.emit('print_output',{'type':'ChoosenOptions', 'output': "The option chosen is ADVANCED_SEARCH"})
    else:
        ADVANCED_SEARCH = 1
        socketio.emit('print_output',{'type':'ChoosenOptions', 'output': "The option chosen is ADVANCED_SEARCH"})
    
    log_str += f"\n\nOptions:\n\nSEARCH_BAR_SCRAPE: {SEARCH_BAR_SCRAPE}\nGENERAL_DEEP_SCRAPE: {GENERAL_DEEP_SCRAPE}\nADVANCED_SEARCH :{ADVANCED_SEARCH}"

    inside_urls1 = []
    inside_urls2 = []
    inside_urls3 = []

    website_urls1 = []
    website_urls2 = []
    website_urls3 = []

    keywords_list = keyword.split(',')

    log_str += "\n" + "#"*20
    
    temp_time = time()

    if SEARCH_BAR_SCRAPE == 1:
        socketio.emit('print_output', {'output': f"Search Bar Scrape is taking place"})
        S = " Search Bar Scrape "
        print("\n\n"+S.center(100, '=')+"\n")
        socketio.emit('print_output', {'output': f"\n\n{S.center(100, '=')}\n"})
        
        base_urls = url

        search_extras = ["?s=", "/search/", "/search?q=", "/topic/"]
        excluded_domains = r'(magicbricks|443|play\.google|facebook\.com|twitter\.com|instagram\.com|linkedin\.com|youtube\.com|\.gov|\.org|policy|terms|buy|horoscope|web\.whatsapp\.com|\.(png|jpg|jpeg|gif|bmp|tiff|webp))'
        result_urls = generate_urls_with_exclusions(base_urls, search_extras, keywords_list, excluded_domains)
        print('\n'.join(result_urls))
       #progress
        socketio.emit('print_output', {'output': '\n'.join(result_urls)})


        search_html = get_html(list(result_urls), mode_of_search="Search Bar Scrape")
        print(f"Failed to get html: {search_html[1]}")
        socketio.emit('print_output', {'output': f"Failed to get html: {search_html[1]}"})

        search_html_content = search_html[0]

        base_url_html_content = get_html(urls=base_urls)[0]
        search_html = prepend_dict(search_html_content, base_url_html_content)
        search_html_pruned = keep_first_occurrence(search_html)

        print("Pruning Completed", len(search_html) - len(search_html_pruned), "Deleted")
        socketio.emit('print_output', {'output': f"Pruning Completed {len(search_html) - len(search_html_pruned)} Deleted"})

    
        urls_list = list(search_html_pruned.keys())
        urls_list_str = ",".join(urls_list)

        scraper = WebScraper2(sub_url_size=1 , keywords=keyword)
        inside_urls, failed_fetch, sub_url_size, total_size = scraper.get_suburls2(urls_list_str)

        # print("Inside URLs:", inside_urls)
        print("Failed Fetch:", failed_fetch)
        print("Splits:", len(inside_urls))
        print("Tree size:", total_size)
        socketio.emit('print_output', {'output': f"Failed Fetch: {failed_fetch}"})
        socketio.emit('print_output', {'output': f"Splits: {len(inside_urls)}"})
        socketio.emit('print_output', {'output': f"Tree size: {total_size}"})


        ## Joining sub urls into one single list
        website_urls1 = inside_urls[1]
        
        print("\n".join(website_urls1[:10]))
        log_str += "#"*20
        log_str += "\nSEARCH BAR SCRAPE"
        log_str += f"Search bar scrape completed in: {time() - temp_time:.2f}s\n"
        log_str += f"Results got: {len(website_urls1)}\n\n"
        log_str += "#"*20
        
    temp_time = time()
    if GENERAL_DEEP_SCRAPE == 1:
        socketio.emit('print_output', {'output': f"General Deep Search is taking place"})

        S = " General Deep Scrape "
        print("\n\n"+S.center(100, '=')+"\n")
        socketio.emit('print_output', {'output': f"\n\n{S.center(100, '=')}\n"})


        ## Extracting sub urls
        urls_list_str = ",".join(url)
        scraper = WebScraper2(sub_url_size = 3 , keywords = keyword)
                    
        inside_urls2, failed_fetch, sub_url_size, total_size2 = scraper.get_suburls2(urls_list_str)
        # print("Inside URLs:", inside_urls)
        print("Failed Fetch:", failed_fetch)
        print("Splits:", len(inside_urls2))
        print("Tree size:", total_size2)
        socketio.emit('print_output', {'output': f"Failed Fetch: {failed_fetch}"})
        socketio.emit('print_output', {'output': f"Splits: {len(inside_urls2)}"})
        socketio.emit('print_output', {'output': f"Tree size: {total_size2}"})


        ## Joining sub urls into one single list
        website_urls2 = [item for sublist in list(inside_urls2.values()) for item in sublist]
        print("\n".join(website_urls2[3:13]))
        log_str += "#"*20
        log_str += "\nGENERAL DEEP SEARCH"
        log_str += f"\nGeneral Deep scrape completed in: {time()-temp_time:.2f}s\n"
        log_str += f"Results got: {len(website_urls2)}\n\n"
        log_str += "#"*20
        
    temp_time = time()
    if ADVANCED_SEARCH == 1:
        socketio.emit('print_output', {'output': f"Advanced Search is taking place"})
        link_results = []

        S = " Advanced Search "
        print("\n\n"+S.center(100, '=')+"\n")
        socketio.emit('print_output', {'output': f"\n\n{S.center(100, '=')}\n"})
        
        Serp_api_list = api_keys.serp_key_list
        Serp_api = get_valid_api_key(Serp_api_list, for_which="Serp")

        # for ad_url in tqdm(url):
        url_split = chunks(url, 2)

        for n, url_ in enumerate(url_split):
            site_url = ["site:" + i for i in url_]
            site_or_url = " OR ".join(site_url)


            params = {
            "q": f"{' '.join(keyword_list)} {site_or_url}",
            "tbm": "nws",
            "api_key": Serp_api,
            "tbs": f"cdr:1,cd_min:{from_date.replace('-', '/')},cd_max:{to_date.replace('-', '/')}",
            'num' : 100
            }

            search = GoogleSearch(params)
            search_dict = search.get_dict()

            #"-".join(from_date.split("-")[:2] + [str((int(from_date.split("-")[2]) + 2))])
            #search.get_dict()['search_information']['news_results_state'] == 'Fully empty'
            try_times = 0
            while search_dict['search_information']['news_results_state'] == 'Fully empty':
                from_date_modified = "-".join(from_date_modified.split("-")[:2] + [str((int(from_date_modified.split("-")[2]) - 2))])
                params['tbs'] = f"cdr:1,cd_min:{from_date_modified},cd_max:{to_date.replace('-', '/')}",
                params['num'] = 70,
                search = GoogleSearch(params)
                search_dict = search.get_dict()
                if try_times == 4 :
                    break

                print(f"From date was modified due to less results: {from_date_modified}")
                try_times += 1
            log_str += "#"*20
            log_str += f"\nADVANCED SEARCH {n}"
            log_str += f"\nFrom date in advaced scrape was modified from {from_date_str} to {from_date_modified}\n\n"

            # import pdb;pdb.set_trace()
            if search_dict['search_information']['news_results_state'] != 'Fully empty':
                link_results += [search_dict['news_results'][i]['link'] for i in range(len(search_dict['news_results']))]
            else: link_results += []

        website_urls3 = link_results
        print("\n".join(website_urls3[:10]))
        
        log_str += f"Results got: {len(website_urls3)}, in {try_times} tries\n"
        log_str += f"Advanced scrape {n} completed in: {time()-temp_time:.2f}s\n\n"
        log_str += "#"*20

    website_urls = website_urls1 + website_urls2 + website_urls3

    log_str += f"\nTotal urls collected: {len(website_urls)}\n"
    log_str += "\n".join(website_urls[:10])

    if len(website_urls) == 0:
        response_complete = "There was nothing to display\n\nKeywords did'nt match any urls\nPlease add additional urls"
    
    else:
        print("length of urls: ",len(website_urls))
        socketio.emit('print_output', {'output': f"Length of URLs: {len(website_urls)}"})


        temp_time = time()

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
        socketio.emit('print_output', {'output': f"date_db_name: {date_db_name}"})
        socketio.emit('print_output', {'output': f"collection_db_name: {collection_db_name}"})
        socketio.emit('print_output', {'output': "Imported Successful"})


        ### Urls of extracted sub urls
        urls_from_extraction = pd.DataFrame(website_urls[:]) 
        urls_from_extraction.columns = ["url"]

        ### Urls that arent yet indexed in db
        df_of_which_to_find_the_date_of = pd.merge(mongo_date_df, urls_from_extraction, how = "outer")
        df_of_which_to_find_the_date_of = df_of_which_to_find_the_date_of.loc[~df_of_which_to_find_the_date_of['Date'].notna(), :] # Dates that are yet found out
        df_of_which_to_find_the_date_of = df_of_which_to_find_the_date_of.drop_duplicates(subset='url', keep='first')              # Dropping duplicates if any

        log_str += f"\nImporting DB from mongo and preprocessing df completed in: {time()-temp_time:.2f}s\n\n"

        temp_time = time()

        S = " Getting Dates for "
        print("\n\n"+S.center(100, '=')+"\n")

        print(f"Dates yet to index: {df_of_which_to_find_the_date_of.shape[0]}")
        socketio.emit('print_output', {'output': f"\n\n{S.center(100, '=')}\n"})
        socketio.emit('print_output', {'output': f"Dates yet to index: {df_of_which_to_find_the_date_of.shape[0]}"})


        list_of_which_to_find_the_date_of = list(df_of_which_to_find_the_date_of["url"].values)

        ### Getting dates for extracted urls that arent indexed in DB
        url_date_list = []
        timeout_seconds = 5

        total_items = len(list_of_which_to_find_the_date_of)
        items_completed = 0
        num_of_output_progress = 10
        for url in tqdm(list_of_which_to_find_the_date_of):
            start_time = time()
            try:
                # Your function to fetch the date from the URL
                date_value = fetch_date_from_url(url)
            except Exception as e:
                # Handle exceptions, e.g., print an error message or store a default value
                print(f"Error fetching date for {url}: {e}")
                socketio.emit('print_output', {'output': f"Error fetching date for {url}: {e}"})

                date_value = None

            elapsed_time = time() - start_time

            # Append to the list if the operation took less than the timeout
            if elapsed_time < timeout_seconds:
                url_date_list.append([url, date_value])
            else:
                print(f"Skipping {url} due to timeout of {timeout_seconds}s")
                socketio.emit('print_output', {'output': f"Skipping {url} due to timeout of {timeout_seconds}s"})
            
            
            items_completed += 1
            if items_completed % (total_items // num_of_output_progress) == 0:
                percentage_complete = (items_completed / total_items) * 100
                socketio.emit('print_output', {'output': f"{progress_bar_once(word='Completed', percentage=round(percentage_complete, 2), num=30)}"})

                

        log_str += f"Amount of dates that needed to be fetched: {len(list_of_which_to_find_the_date_of)}\n"
        log_str += f"Dates fetching completed in: {time()-temp_time:.2f}s\n\n"
        url_date_dict = {i[0] : i[1] for i in url_date_list}
        

        # Insert the document into the collection
        temp_time = time()
        S = " Indexing to Database "
        print("\n\n"+S.center(100, '=')+"\n")
        socketio.emit('print_output', {'output': f"\n\n{S.center(100, '=')}\n"})


        data = url_date_dict
        date_db_name = "PetraOil"
        collection_db_name = "Date Database"


        save_to_mongo(date_db_name, collection_db_name, data = data)

        log_str += f"Dated Indexed back to mongo in: {time()-temp_time:.2f}s\n\n"

        urls_date_df = pd.merge(urls_from_extraction, mongo_date_df, on='url', how='inner').sort_values(by="Date",ascending=False)
        # urls_date_df.to_csv('url_date.csv')

        # Columns
        print(urls_date_df.columns)
        socketio.emit('print_output', {'output': f"Columns: {', '.join(urls_date_df.columns)}"})

        plot_date(urls_date_df, save_path=f"Plots/{datetime.now()}.jpg")

        # print(urls_date_df.isna().sum())

        S = " Filtering by date "
        print("\n\n"+S.center(100, '=')+"\n")
        socketio.emit('print_output', {'output': '=' * 100})


        start_date = pd.to_datetime(from_date_modified,format='%d-%m-%Y')
        end_date = pd.to_datetime(to_date,format='%d-%m-%Y')
        df_filtered_by_date = df_filtered_by_date = urls_date_df[(urls_date_df["Date"] >= start_date) & (urls_date_df["Date"] <= end_date)]
        
        try_times = 0
        while len(df_filtered_by_date) < 2:
            start_date = pd.to_datetime(from_date_modified,format='%d-%m-%Y')
            df_filtered_by_date = urls_date_df[(urls_date_df["Date"] >= start_date) & (urls_date_df["Date"] <= end_date)]
            from_date_modified = "-".join(from_date_modified.split("-")[:2] + [str((int(from_date_modified.split("-")[2]) - 2))])
            df_filtered_by_date = df_filtered_by_date = urls_date_df[(urls_date_df["Date"] >= start_date) & (urls_date_df["Date"] <= end_date)]

            if try_times == 4:
                break
            try_times += 1
        
        print(f"Amount of urls between the dates: {df_filtered_by_date.shape[0]}")
        socketio.emit('print_output', {'output': f"Amount of urls between the dates: {df_filtered_by_date.shape[0]}"})


        log_str += f"Amount of urls between the dates: {df_filtered_by_date.shape[0]}\n\n"

        if df_filtered_by_date.shape[0] >= 0:

            date_db_name = "PetraOil"
            collection_db_name = "Html Database"
            columns = ["url", "Html"]
            mongo_html_df = import_from_mongo(date_db_name, collection_db_name, columns)

            df_of_which_to_find_the_html_of = pd.merge(mongo_html_df, pd.DataFrame(df_filtered_by_date["url"]) , how = "outer")
            df_of_which_to_find_the_html_of = df_of_which_to_find_the_html_of.loc[~df_of_which_to_find_the_html_of['Html'].notna(), :] # Dates that are yet found out
            df_of_which_to_find_the_html_of = df_of_which_to_find_the_html_of.drop_duplicates(subset='url', keep='first')              # Dropping duplicates if any

            print(f"Html yet to index: {df_of_which_to_find_the_html_of.shape[0]}")
            socketio.emit('print_output', {'output': f"Html yet to index: {df_of_which_to_find_the_html_of.shape[0]}"})


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
            socketio.emit('print_output', {'output': "\n\n" + '=' * 100 + "\n"})

            
            temp_time = time()

            url_html_df_date_sorted = mongo_html_df[mongo_html_df['url'].isin(list(df_filtered_by_date["url"]))]

            if SORT_BY_RELAVANCY == 1:
                if len(url_html_df_date_sorted) == 0:
                    response_complete = "There was an issue with indexing dates \n\n or, links and keywords were provided incorrectly"

                else:
                    url_html_df_date_sorted = rerank_df(df = url_html_df_date_sorted, col_to_rank="Html", col_to_address="url", query= " ".join(keywords_list) , pprint=True, api_key=api_keys.cohere_key_list[0]) #.iloc[:,:2]
                log_str += f"Sorting completed in {time()-temp_time:.2f}s"

            # url_html_df_date_sorted.to_csv("url_Html2.csv", index = False)
            if len(url_html_df_date_sorted) != 0:
                sources_str = "\n\n".join(list(url_html_df_date_sorted.url)[:20])

                page = 1
                amount_of_content = 20
                url_html_df_date_sorted_20 = url_html_df_date_sorted[(page - 1) * amount_of_content : amount_of_content * page]  # Only 10 at a time

                dashboard(urls_date_df, url_html_df_date_sorted_20, from_date, to_date, amount_of_content)

                print(f"Relavancy Score of page number: {page} is: {url_html_df_date_sorted_20.Relevance_Score.median():.3f}")
                socketio.emit('print_output', {'output': f"Relavancy Score of page number: {page} is: {url_html_df_date_sorted_20.Relevance_Score.median():.3f}"})


                url_html_dict = url_html_df_date_sorted_20.set_index('url')['Html'].to_dict()
                url_html_dict = {key : clean_and_extract(value) for key,value in url_html_dict.items()}  # Cleaning the Text
                
                # url_html_df = pd.DataFrame(list(url_html_dict.items()), columns=['url', 'Html'])
                # url_html_df.to_csv("url_Html.csv", index = False)

                try:
                    del url_html_extracted["_id"]
                    print("Deleted _id")
                    socketio.emit('print_output', {'output': 'Deleted _id'})

                except:
                    pass

                url_extracted_html = kep(website_content = url_html_dict, keywords = " ", filter_by_amount = 30)
                # url_extracted_html = url_html_dict

                url_html_content_txt = ''
                for key, val in url_extracted_html.items():
                    url_html_content_txt += key + '\n\n' + val + '\n\n' + '-'*50 + '\n\n'

                with open(f"Output text/{india_time}.txt", "w") as f:
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
                socketio.emit('print_output', {'output': '\n\n'+ '='.center(100, '=') + '\n'})


                question = prompt
                print(f"Itterations: {iterations}")
                socketio.emit('print_output', {'output': f"Iterations: {iterations}"})

                response_complete = ''

                temp_time = time()

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
                    socketio.emit('print_output', {'output': f"Batch {data_idx + 1} out of {iterations} completed"})

                log_str += f"\nOpenai execution of {iterations} itteration completed in {time()-temp_time:.2f}s"

        else:
            response_complete = "There was nothing to display\n\nURLS dont exist within the particular Time frame\nPlease try expanding the time frame and try again"

        # print(response_complete)

    
    app_end_time = time()
    
    print(f"Completed in {app_end_time - app_start_time :.2f}s")
    socketio.emit('print_output', {'output': f"Completed in {app_end_time - app_start_time:.2f}s"})





    response_data = {"url" : url}


    response_complete = response_complete.strip()
    response_complete_clickable = make_links_clickable(response_complete)
    response_complete_clickable = response_complete_clickable.replace('\n', '<br>')
    sources = make_links_clickable(sources_str).replace('\n', '<br>')

    session['result_content'] = Markup(response_complete_clickable)
    session['sources_content']=Markup(sources);


    log_str += f"\n\nTotal time: {time() - app_start_time:.2f}s"

    with open("Logs.txt" , "w") as f:
        f.write(log_str)

    # Logs
    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = dev_emal
    message["Subject"] = f"Subject: {india_time}"

    # Add body to email
    message.attach(MIMEText(log_str, "plain"))

    # Open the image file and attach it to the email
    with open("dashboard/dashboard_plot.png", "rb") as attachment:
        image_part = MIMEImage(attachment.read(), name="dashbaord.jpg")

    # Add image to the email
    message.attach(image_part)

    context = ssl.create_default_context(cafile=certifi.where())

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())




    # sender_email = "bat463660@gmail.com"
    # sender_password = "bygc aape tnem adev"
    # receiver_email = "mohdmafaz200303@gmail.com"
    subject = f"Subject: {india_time}.txt"
    body = "Text File"
    attachment_path = f"Output text/{india_time}.txt"
    send_email(sender_email, sender_password, receiver_email, subject, body, attachment_path)



    return redirect('/result')
    


@app.route('/result')
def result():
      result_data = session.get('result_content', None);
      sources_data=session.get('sources_content',None);
    #   print("result_data before rendering template:", result_data)
      return render_template('result2.html', result_data=result_data,sources_data=sources_data)



@app.route('/display_image')
def display_image():
    image_path = os.path.join(app.root_path, 'dashboard', 'dashboard_plot.png')
    print(f"Absolute Path: {image_path}")
    return send_from_directory('dashboard', 'dashboard_plot.png')


if __name__ == '__main__':
     socketio.run(app)
    # app.run(debug=True)
