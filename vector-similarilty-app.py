from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# API Configuration
AI_PROXY_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMzMDAwMDkwQGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.Z9TWR3dvVwBfx2BCRG6mrAPA7pyYe8tbB_nnXEJ8-WA"
AI_PROXY_URL = "https://aiproxy.sanand.workers.dev/openai/v1/embeddings" 

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Updated Pydantic models to match the actual request format
class SimilarityRequest(BaseModel):
    docs: List[str]  # Changed from 'documents' to 'docs'
    query: str

class SimilarityResponse(BaseModel):
    matches: List[str]

def get_embedding(text: str) -> List[float]:
    """Get embeddings for a given text using AI Proxy service."""
    headers = {
        "Authorization": f"Bearer {AI_PROXY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "text-embedding-3-small",
        "input": text
    }
    
    try:
        response = requests.post(AI_PROXY_URL, headers=headers, json=payload)
        response.raise_for_status()
        embedding_data = response.json()
        return embedding_data["data"][0]["embedding"]
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting embedding: {str(e)}")

@app.post("/similarity", response_model=SimilarityResponse)
async def find_similar_documents(request: SimilarityRequest):
    try:
        logger.info(f"Processing similarity request for query: {request.query}")
        
        # Get query embedding
        query_embedding = get_embedding(request.query)
        
        # Get embeddings for all documents
        doc_embeddings = []
        for doc in request.docs:  # Changed from request.documents to request.docs
            embedding = get_embedding(doc)
            doc_embeddings.append(embedding)
        
        # Find most similar documents
        similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
        top_indices = np.argsort(similarities)[-3:][::-1]
        
        # Return the contents of the most similar documents
        matches = [request.docs[i] for i in top_indices]  # Changed from request.documents to request.docs
        
        return SimilarityResponse(matches=matches)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)