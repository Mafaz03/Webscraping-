# Importing necessary libraries and modules
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Loading environment variables from a .env file
load_dotenv()

# Fetching MongoDB URI from environment variables
mongo_uri = os.getenv("mongo")

# Establishing a connection to the MongoDB server
client = MongoClient(mongo_uri)

# Accessing the specified database and collection
db = client.get_database(os.getenv("db_name"))
collection = db.get_collection("news")

# Function to update data in the MongoDB collection
def update_data(url, date):
    # Creating a dictionary with URL and date
    data = {
        "url": url,
        "date": date
    }

    # Inserting the data into the MongoDB collection
    collection.insert_one(data)

# Example usage of the update_data function
update_data("test_url", "dd/mm/yyyy")
