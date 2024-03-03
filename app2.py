# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    urls = data.get('urls')
    keyword = data.get('keyword')

  
    response_data = {
        'status': 'success',
        'message': 'Scraping initiated successfully.',
        'urls': urls,
        'keyword': keyword,
        'processing_complete': True,  # Add a flag for processing completion
    }


    return redirect(url_for('result', urls=urls, keyword=keyword, processing_complete=True))

@app.route('/result')
def result():
    urls = request.args.get('urls')
    keyword = request.args.get('keyword')
    processing_complete = request.args.get('processing_complete', False)

    return render_template('result.html', urls=urls, keyword=keyword, processing_complete=processing_complete)

if __name__ == '__main__':
    app.run(debug=True)
