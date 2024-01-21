# Importing the Flask module
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Creating a Flask web application
app = Flask(__name__)

# Route for the home page
@app.route('/')
def index():
    # Rendering the 'index.html' template for the home page
    return render_template('index.html')

# Route for handling the scraping process
@app.route('/scrape', methods=['POST'])
def scrape():
    # Getting JSON data from the request
    data = request.get_json()
    
    # Extracting URLs and keyword from the JSON data
    urls = data.get('urls')
    keyword = data.get('keyword')

    # Preparing response data with a success message and processing flag
    response_data = {
        'status': 'success',
        'message': 'Scraping initiated successfully.',
        'urls': urls,
        'keyword': keyword,
        'processing_complete': True,  # Add a flag for processing completion
    }

    # Redirecting to the result route and passing along necessary parameters
    return redirect(url_for('result', urls=urls, keyword=keyword, processing_complete=True))

# Route for displaying the result
@app.route('/result')
def result():
    # Retrieving parameters from the request URL
    urls = request.args.get('urls')
    keyword = request.args.get('keyword')
    processing_complete = request.args.get('processing_complete', False)

    # Rendering the 'result.html' template with the provided parameters
    return render_template('result.html', urls=urls, keyword=keyword, processing_complete=processing_complete)

# Running the Flask app if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
