from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Country Outline API.",
        "usage": "Use the endpoint /api/outline?country=CountryName to fetch the outline.",
        "example": "/api/outline?country=India"
    }

@app.get("/api/outline")
async def get_country_outline(country: str = Query(..., description="Country name to fetch from Wikipedia")):
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code != 200:
        return {"error": f"Could not fetch Wikipedia page for {country}"}
    
    soup = BeautifulSoup(response.content, "lxml")
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    markdown_outline = "## Contents\n\n"
    markdown_outline += f"# {country}\n\n"

    for heading in headings:
        level = int(heading.name[1])
        title = heading.get_text(strip=True)
        if title.lower() == "jump to content":
            continue
        markdown_outline += f"{'#' * level} {title}\n\n"

    return {"outline": markdown_outline}

