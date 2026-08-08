#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 16:35:46 2026

@author: gustavo
"""

from pathlib import Path
import json
from llama_index.core import Document, VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama


# Initialize the embedding model
embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    request_timeout=300.0,  # Increased timeout for large documents
)

# Initialize the LLM with optimized settings
llm = Ollama(
    model="llama3.2:latest",  # Confirm with `ollama list`
    request_timeout=300.0,
    temperature=0.1,          # Lower temperature for more factual responses
)

# Set global configurations
Settings.embed_model = embed_model
Settings.llm = llm
Settings.chunk_size = 1024    # Default: good for most documents
Settings.chunk_overlap = 200  # Maintains context between chunks

def load_and_index_documents(data_dir="data"):
    """Load documents and create vector index"""

    # Check if data directory exists
    #if not Path(data_dir).exists():
    #    raise FileNotFoundError(f"Data directory '{data_dir}' not found. Please create it and add your PDF files.")
        
    # load the data from the KG
    with open("title_description.json", "r", encoding="utf-8") as f:
        data = json.load(f)


        # Convert JSON records into LlamaIndex documents
        documents = []
    
        for item in data:
            documents.append(
                Document(
                    text=item["description"],
                    metadata={
                        "title": item.get("title", "")
                    }
                )
            )

    # Load documents from the data folder
    #docs = SimpleDirectoryReader(data_dir).load_data()

    #if not docs:
    #    raise ValueError(f"No documents found in {data_dir}")


    # Build vector index from documents
    #index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
    
    print(f"Loaded {len(documents)} documents")


    # Create vector index
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=embed_model
    )

    return index

def create_query_engine(index, similarity_top_k=3):
    """Create query engine with specified retrieval parameters"""

    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=similarity_top_k,  # Number of relevant chunks to retrieve
        response_mode="compact"             # Compact response generation
    )

    return query_engine

def test_rag_system():
    """Test the RAG system with sample queries"""

    try:
        # Load documents and create index
        index = load_and_index_documents()

        # Create query engine
        query_engine = create_query_engine(index)

        # Sample test queries
        test_queries = [
            #"Summarize this document in 3 lines",
            #"What are the main topics covered in these documents?",
            "Resume estos documentos en tres líneas",
            "¿Cuáles son los principales temas tratados en estos documentos?",
            "¿Qué personalidades se mencionan en estos documentos?",
            "¿Qué países se mencionan principalmenet en estos documentos?"
        ]

        print("RAG System Test Results")
        print("=" * 50)

        for i, query in enumerate(test_queries, 1):
            print(f"\nTest {i}: {query}")
            print("-" * 40)

            try:
                response = query_engine.query(query)
                print(f"Response: {response}")
                print(f"Status: SUCCESS")
            except Exception as e:
                print(f"Error: {str(e)}")
                print(f"Status: FAILED")

            print("-" * 40)

        return True

    except Exception as e:
        print(f"System Error: {str(e)}")
        return False

# Main execution
if __name__ == "__main__":

    print("Starting RAG Pipeline Test...")

    # Test the complete system
    success = test_rag_system()

    if success:
        print("\nRAG system is working correctly!")
        print("You can now use the query_engine to ask questions about your documents.")
    else:
        print("\nRAG system test failed. Check the error messages above.")

