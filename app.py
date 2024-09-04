from flask import Flask, request, jsonify
import os
import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

app = Flask(__name__)

# Load the pre-trained sentence transformer model
print("Loading sentence transformer model...")
retriever_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Sentence transformer model loaded successfully.")

# Initialize the FAISS index and model components
index = None
corpus = []

# Function to extract text from PDFs
def extract_text_from_pdfs(folder_path):
    print(f"Extracting text from PDFs in folder: {folder_path}")
    extracted_texts = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            text = ""
            try:
                with open(file_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
                if text:
                    extracted_texts.append(text)
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
    print("Text extraction completed.")
    return extracted_texts

# Function to initialize the retrieval index
def initialize_index():
    global index, corpus
    pdf_folder_path = "data"
    
    print("Initializing retrieval index...")
    # Extract text from all PDFs in the folder
    corpus = extract_text_from_pdfs(pdf_folder_path)

    # Encode the corpus
    print("Encoding corpus...")
    corpus_embeddings = retriever_model.encode(corpus, convert_to_tensor=True)

    # Initialize FAISS index
    print("Initializing FAISS index...")
    dimension = corpus_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(corpus_embeddings.numpy())
    print("FAISS index initialized successfully.")

# Load the language model and tokenizer
print("Loading language model...")
model_name = "t5-base"  
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
print("Language model loaded successfully.")

# Function to retrieve documents and generate responses
def retrieve_and_generate(query, top_k=3):
    print(f"Processing query: '{query}'")
    query_embedding = retriever_model.encode([query], convert_to_tensor=True)

    distances, indices = index.search(query_embedding.numpy(), top_k)

    retrieved_docs = [corpus[idx] for idx in indices[0]]
    context = " ".join(retrieved_docs)

    input_text = f"question: {query} context: {context}"
    inputs = tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=150, num_beams=2, early_stopping=True)
    
    # Set `clean_up_tokenization_spaces` explicitly to avoid the warning
    generated_response = tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)

    print("Query processed successfully.")
    return generated_response


@app.route('/query', methods=['POST'])
def handle_query():
    print("Received a new query request.")
    data = request.json
    query = data.get('query', '')

    if not query:
        print("Error: No query provided.")
        return jsonify({'error': 'No query provided'}), 400

    try:
        response = retrieve_and_generate(query)
        print("Sending response back to client.")
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting the application...")
    initialize_index()
    print("Application is running.")
    app.run(host='0.0.0.0', port=5000, debug=True)
