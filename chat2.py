from flask import Flask, render_template, request

from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import os
import tkinter as tk
from tkinter import filedialog
import time

os.environ["OPENAI_API_KEY"] = "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"

# Function to open file dialog and get selected files
def get_file_paths():
    root = tk.Tk()
    root.withdraw()

    # Set initial directory to "Output text"
    initial_dir = "Output text"

    file_paths = filedialog.askopenfilenames(
        title="Select Files",
        filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")],
        initialdir=initial_dir,

    )
    return file_paths

# Get file paths from the user
file_paths = get_file_paths()
print(file_paths);
# Read text from selected files
raw_text = ""
for file_path in file_paths:
    if file_path.endswith(".pdf"):
        pdf_reader = PdfReader(file_path)
        for i, page in enumerate(pdf_reader.pages):
            content = page.extract_text()
            if content:
                raw_text += content
    elif file_path.endswith(".txt"):
        with open(file_path, "r") as f:
            raw_text += f.read()

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

# Flask app setup
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

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

if __name__ == "__main__":
    app.run()
