from pymongo import MongoClient
import certifi
import pandas as pd
import numpy as np

ca = certifi.where()

def import_from_mongo(date_db_name, collection_db_name, columns):
    """
    Imports data from a MongoDB collection specified by the date database name and collection name.

    Parameters:
    - date_db_name (str): The name of the date database in MongoDB.
    - collection_db_name (str): The name of the collection within the date database.

    Returns:
    - pd.DataFrame: A Pandas DataFrame containing the imported data.

    """

    client = MongoClient("mongodb+srv://Mafaz2:mafaz@petra.ewsack2.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=ca)

    db = client[date_db_name]
    collection = db[collection_db_name]


    mongo_df = pd.DataFrame(collection.find()).transpose()[1:].reset_index()                        # Importing all Data from Date Database collection
    Nan_to_empty_str = mongo_df.fillna('')                                                          # Nan to ''
    list_of_extra_cols = list(range(Nan_to_empty_str.shape[1] - 1))                                 # Extra columns caused due to mongodb 
    Nan_to_empty_str[columns[1]] = np.array(Nan_to_empty_str[list_of_extra_cols]).sum(axis=1)       # Adding rows row wise
    mongo_df = Nan_to_empty_str.drop(list_of_extra_cols, axis = 1)                                  # Removing extra columns
    if columns[1] == "Date":
        mongo_df['Date'] = pd.to_datetime(mongo_df['Date'], dayfirst=True, infer_datetime_format=True, errors='coerce')  # Converting Date to Datetime
        mongo_df = mongo_df.sort_values(by='Date', ascending=False)                                 # Sorting by Date
    mongo_df.columns = columns                                                                      # Renaming Column name
    mongo_df = mongo_df.dropna()                                                                    # Dropping Null values from mongo (most probably not useful urls)
    return mongo_df
"""
## Example usecase:
date_db_name = "PetraOil"
collection_db_name = "Date Database"
columns = ["url", "Date"]
print(import_from_mongo(date_db_name, collection_db_name, columns))
"""


def save_to_mongo(date_db_name, collection_db_name, data):
    """
    Saves data to a MongoDB collection specified by the date database name and collection name.

    Parameters:
    - date_db_name (str): The name of the date database in MongoDB.
    - collection_db_name (str): The name of the collection within the date database.
    - data: The data to be inserted into the MongoDB collection.
    """
    try:

        client = MongoClient("mongodb+srv://Mafaz2:mafaz@petra.ewsack2.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=ca)

        db = client[date_db_name]
        collection = db[collection_db_name]

        insert_doc = collection.insert_one(data)
        print(f"Inserted in Mongodb Cloud\nDatabase: {date_db_name}\nCollection: {collection_db_name}")

    except Exception as e:
        print(e)


"""
## Example usecase:
data = url_date_dict
date_db_name = "PetraOil"
collection_db_name = "Date Database"
save_to_mongo(date_db_name, collection_db_name, data = data)

"""
