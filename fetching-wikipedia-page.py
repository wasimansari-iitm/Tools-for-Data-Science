from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/outline")
async def get_country_outline(country: str):
    # Fetch the Wikipedia page
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Country not found")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract headings
    headings = []
    for i in range(1, 7):  # H1 to H6
        for heading in soup.find_all(f'h{i}'):
            level = '#' * i  # Markdown heading level
            headings.append(f"{level} {heading.get_text(strip=True)}")

    # Create the Markdown outline
    markdown_outline = "## Contents\n\n" + "\n".join(headings)
    return JSONResponse(content={"outline": markdown_outline})