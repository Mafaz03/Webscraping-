import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup
from unidecode import unidecode

# You might need to download these NLTK packages if you haven't already
# nltk.download('stopwords')
# nltk.download('wordnet')

def clean_text(text):
    # Remove HTML tags and markup
    text = BeautifulSoup(text, "html.parser").get_text()
    
    # Remove URLs and email addresses
    text = re.sub(r'(https?:\/\/[^\s]+|www\.[^\s]+|[^\s]+@[^\s]+)', '', text)
    
    # Remove special characters and symbols
    text = re.sub(r'\W+', ' ', text)
    
    # Remove numerical digits
    text = re.sub(r'\d+', '', text)
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove accents and perform case normalization
    text = unidecode(text).lower()
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word not in stop_words])
    
    # Perform lemmatization
    lemmatizer = WordNetLemmatizer()
    text = ' '.join([lemmatizer.lemmatize(word) for word in text.split()])
    
    return text

# Example usage:
text = "<p>This is s0me j#nk text with an email test@example.com and a URL https://example.com.   Wh@t do y0u think?</p>"
print(clean_text(text))
