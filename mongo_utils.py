from pymongo import MongoClient
import certifi
import pandas as pd
import numpy as np

# Specify the location of the CA certificate file
ca = certifi.where()

def import_from_mongo(date_db_name: str, collection_db_name: str, columns: list) -> pd.DataFrame():
    """
    Imports data from a MongoDB collection specified by the date database name and collection name.

    Parameters:
    - date_db_name (str): The name of the date database in MongoDB.
    - collection_db_name (str): The name of the collection within the date database.

    Returns:
    - pd.DataFrame: A Pandas DataFrame containing the imported data.
    """

    # Connect to the MongoDB Atlas cluster using the provided credentials and CA certificate
    client = MongoClient("mongodb+srv://Mafaz2:mafaz@petra.ewsack2.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)

    db = client[date_db_name]
    collection = db[collection_db_name]

    # Import data from MongoDB, transpose, and handle additional columns caused by MongoDB
    mongo_df = pd.DataFrame(collection.find()).transpose()[1:].reset_index()
    Nan_to_empty_str = mongo_df.fillna('') 
    list_of_extra_cols = list(range(Nan_to_empty_str.shape[1] - 1))
    Nan_to_empty_str[columns[1]] = np.array(Nan_to_empty_str[list_of_extra_cols]).sum(axis=1)
    mongo_df = Nan_to_empty_str.drop(list_of_extra_cols, axis=1)

    # Handle date-specific processing if the column is "Date"
    if columns[1] == "Date":
        mongo_df['Date'] = pd.to_datetime(mongo_df['Date'], dayfirst=True, infer_datetime_format=True, errors='coerce')
        mongo_df = mongo_df.sort_values(by='Date', ascending=False)

    mongo_df.columns = columns
    mongo_df = mongo_df.dropna()
    return mongo_df

"""
## Example usecase:
date_db_name = "PetraOil"
collection_db_name = "Date Database"
columns = ["url", "Date"]
print(import_from_mongo(date_db_name, collection_db_name, columns))
"""

def save_to_mongo(date_db_name: str, collection_db_name: str, data):
    """
    Saves data to a MongoDB collection specified by the date database name and collection name.

    Parameters:
    - date_db_name (str): The name of the date database in MongoDB.
    - collection_db_name (str): The name of the collection within the date database.
    - data: The data to be inserted into the MongoDB collection.
    """
    try:
        # Connect to the MongoDB Atlas cluster using the provided credentials and CA certificate
        client = MongoClient("mongodb+srv://Mafaz2:mafaz@petra.ewsack2.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)

        db = client[date_db_name]
        collection = db[collection_db_name]

        # Insert data into the MongoDB collection
        insert_doc = collection.insert_one(data)
        print(f"Inserted in Mongodb Cloud\nDatabase: {date_db_name}\nCollection: {collection_db_name}")

    except Exception as e:
        print(e)

"""
## Example usecase:
data = url_date_dict
date_db_name = "PetraOil"
collection_db_name = "Date Database"
save_to_mongo(date_db_name, collection_db_name, data=data)
"""
