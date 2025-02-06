import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

# Load the JSON file
current_dir = os.path.dirname(__file__)  # Get the directory of the current script
json_file_path = os.path.join(current_dir, "q-vercel-python.json")  # Construct the path to marks.json

with open(json_file_path, "r") as f:  # Open the JSON file
    data = json.load(f)  # Load the data from the file

# Create a dictionary for quick lookups
marks_dict = {item['name']: item['marks'] for item in data}

# Create FastAPI instance
app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
async def get_marks(name: Optional[List[str]] = Query(None)):
    if name:
        marks = [marks_dict.get(n, 0) for n in name]  # Default to 0 if not found
    else:
        marks = []

    return {"marks": marks}
