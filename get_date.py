import requests
from htmldate import find_date
from datetime import datetime

def fetch_date_from_url(url: str):
    """
    This function fetches the date from a webpage.

    It sends a GET request to the provided URL, retrieves the HTML content, and attempts to find a date using the htmldate library.
    If a date is found, it converts the date into the 'day-month-year' format and returns it; if not, it returns None.
    If an error occurs during the process, it prints an error message and returns None.

    Args:
    url (str): The URL of the webpage to fetch the date from.

    Returns:
    formatted_date (str): The date of the article in 'dd-mm-yyyy' format, or None if no date is found or an error occurs.
    """
    try:
        # Send a GET request to the URL and retrieve the HTML content
        html = requests.get(url).content.decode('utf-8')
        
        # Attempt to find a date in the HTML content
        date = find_date(html)
        
        if date is None:
            # If no date is found, return None
            return None
        else:
            # Convert the date string into a datetime object
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            # Convert the datetime object into the desired format
            formatted_date = date_obj.strftime("%d-%m-%Y")
            
            # Return the formatted date
            return formatted_date
    except Exception as e:
        # Print an error message and return None in case of an error
        print("An error occurred:", str(e))
        return None
    
# Example usage:
# url = "https://constructionreviewonline.com/concrete/how-permanent-christmas-lights-can-transform-your-phoenix-home/"
# print(fetch_date_from_url(url=url))

