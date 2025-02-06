import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Read the CSV file
df = pd.read_csv('q-fastapi.csv')

# Create FastAPI app
app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api")
async def get_students(request: Request):
    # Get all query parameters
    params = request.query_params

    # If no class filter is provided, return all students
    if 'class' not in params:
        return {"students": df.to_dict(orient='records')}
    
    # Get all class values
    classes = params.getlist('class')
    
    # Filter students by specified classes
    filtered_students = df[df['class'].isin(classes)].to_dict(orient='records')
    
    return {"students": filtered_students}

# Run with: uvicorn main:app --reload