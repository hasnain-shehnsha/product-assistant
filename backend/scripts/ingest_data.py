import os
import uuid
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../..', '.env'))

def main():
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "products")
    
    if not api_key:
        print("PINECONE_API_KEY is missing from environment variables.")
        return

    pc = Pinecone(api_key=api_key)
    
    # Check if index exists, if not create it
    if index_name not in pc.list_indexes().names():
        print(f"Creating index {index_name}...")
        pc.create_index(
            name=index_name,
            dimension=384, # all-MiniLM-L6-v2 dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        
    index = pc.Index(index_name)
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load PDFs from data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    print(f"Loading PDFs from {data_dir}...")
    loader = PyPDFDirectoryLoader(data_dir)
    documents = loader.load()
    
    if not documents:
        print("No documents found in the data directory.")
        return
        
    print(f"Loaded {len(documents)} document pages.")
    
    # Chunk the documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")
    
    print("Generating embeddings and upserting data...")
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        vectors = []
        for chunk in batch:
            vector = embeddings_model.embed_query(chunk.page_content)
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": vector,
                "metadata": {
                    "text": chunk.page_content,
                    "source": chunk.metadata.get("source", "unknown"),
                    "page": chunk.metadata.get("page", 0)
                }
            })
        index.upsert(vectors=vectors)
        print(f"Upserted batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
        
    print("Successfully ingested PDF data into Pinecone!")

if __name__ == "__main__":
    main()
