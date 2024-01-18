# Webscraping:
Repo for Petra Oil Bitumen 

## Introduction
The Petra Oil Web Scraper is a proprietary Python-based tool developed to streamline data extraction from websites. This documentation serves as a comprehensive guide to its functionalities, setup, and usage.

## Overview
This scraper is purpose-built to extract internal links from specified websites, perform keyword searches within the extracted links, and provide detailed information based on user-defined queries.

## Key Features
### Link Extraction
Description: Extracts internal links from targeted websites.
Implementation: Utilizes Python libraries for web scraping, navigating the HTML structure to identify anchor tags.

### Keyword Search
Description: Conducts keyword searches within the extracted links.
Implementation: Employs advanced string matching algorithms to locate defined keywords within the link set.

### Information Prompt
Description: Allows users to request specific details related to keywords or website content.
Implementation: Utilizes user-input queries to generate targeted responses based on search results or website content.

### Duplicate Elimination
Description: Filters and eliminates duplicate links obtained during the scraping process.
Implementation: Employs robust data structures to ensure uniqueness and prevent redundancy in the list of extracted links.

### Depth Configuration
Description: Allows customization of link traversal depth.
Implementation: Utilizes a tree traversal mechanism to control the exploration depth within the link structure.

### Web Interface (Current State)
Description: The current iteration of the web interface boasts an expertly crafted user experience, driven primarily by JavaScript functionalities.

Implementation: Developed with a predominant focus on JavaScript to ensure an interactive and dynamic user interface. Leveraging modern JavaScript frameworks and methodologies, the interface delivers a sophisticated yet intuitive user experience. Its responsive design and seamless interaction cater to diverse user needs, providing a comprehensive platform for efficient data input and retrieval.
## Usage Instructions

### Interacting with the Scraper
Input: Provide the website link for link extraction and keyword search.
Define Keywords: Set specific keywords for the search operation.
Depth Configuration: Customize the depth parameter for link traversal.
Prompt Information: Enter queries for specific information related to keywords or website content.

### Output
1.Retrieved links from the provided website.
2.Keyword search results highlighting occurrences within the extracted links.
3.Prompted information based on user queries.

## Development Setup
### Prerequisites
Python environment with required dependencies.
MongoDB instance for storing extracted data.

### Required Dependencies
Python Libraries: See the requirements.txt file for a comprehensive list of required Python libraries and their versions necessary for the scraper's operation. Install them using pip install -r requirements.txt.

### Database Configuration
The scraper utilizes MongoDB for storing extracted data.
Installation: Install MongoDB and set up a local or remote instance.
Configuration: Update the MongoDB connection settings in the config.py file to specify the database connection details such as hostname, port, username, and password

## Contribution Guidelines
This is a private repository; contributions are restricted to authorized team members only.
## License
This project is a proprietary system owned by Petra Oil Bitumen and is not open to the public.

