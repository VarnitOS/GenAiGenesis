import os
import cohere
import chromadb
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

# Initialize Cohere client
co = cohere.Client(os.environ.get('COHERE_API_KEY'))

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

def embed_text(text):
    """Generate embeddings for the provided text using Cohere"""
    response = co.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_document"
    )
    return response.embeddings[0]

def store_embedding_in_chromadb(embedding, metadata):
    """Store the embedding in ChromaDB"""
    collection = chroma_client.get_or_create_collection(name="pdf_embeddings")
    collection.add(
        documents=[metadata['filename']],
        embeddings=[embedding],
        ids=[metadata["filename"]]
    )

def fetch_stored_data():
    """Retrieve stored data from ChromaDB"""
    collection = chroma_client.get_or_create_collection(name="pdf_embeddings")
    stored_data = collection.get()
    print("Stored Data:", stored_data)

def clear_collection():
    """Clear all data from the 'pdf_embeddings' collection"""
    # collection = chroma_client.get_or_create_collection(name="pdf_embeddings")
    chroma_client.delete_collection(name="pdf_embeddings")  # Deletes all entries
    print("Cleared all data from the collection.")


def main(pdf_path):
    clear_collection()
    """Main function to process the PDF and store embeddings"""
    text = extract_text_from_pdf(pdf_path)
    embedding = embed_text(text)
    metadata = {"filename": os.path.basename(pdf_path)}
    store_embedding_in_chromadb(embedding, metadata)
    print(f"Successfully embedded and stored {pdf_path}")
    fetch_stored_data()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python embed_pdf.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    main(pdf_path)
