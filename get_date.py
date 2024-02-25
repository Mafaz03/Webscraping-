import requests
from htmldate import find_date
from datetime import datetime

def fetch_date_from_url(url):
    """
    This function fetches the date from a webpage.

    It prompts the user to enter a URL, sends a GET request to that URL, and attempts to find a date in the HTML content of the webpage.
    If a date is found, it converts the date into the 'day-month-year' format and prints it; if not, it prints 'Date not found'.
    If an error occurs during the process, it prints 'An error occurred' along with the error message.

    Args:
    url (str) = string of url needed to find date of.

    Returns:
    formatted_date(Datetime) = date of article (if exist)
    """
    
    try:
        html = requests.get(url).content.decode('utf-8')
        date = find_date(html)
        if date is None:
            # print("Date not found")
            return None
        else:
            # Convert the date string into a datetime object
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            # Convert the datetime object into the desired format
            formatted_date = date_obj.strftime("%d-%m-%Y")

            # data={
            #     url:url,
            #     date:formatted_date
            # }
            # writeone
            
            return formatted_date
    except Exception as e:
        
        # data={
            #     url:url,
            #     date:formatted_date
            # }
            # writeone
        
        print("An error occurred:", str(e))
        return None
    
    
"""
## Example Usecase:
url = "https://constructionreviewonline.com/concrete/how-permanent-christmas-lights-can-transform-your-phoenix-home/"
print(fetch_date_from_url(url = url))
"""
