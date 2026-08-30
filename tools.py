import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv
from langchain.tools import tool


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError(
        "TAVILY_API_KEY is not configured in the .env file."
    )


# ============================================================
# TAVILY CLIENT
# ============================================================

tavily = TavilyClient(
    api_key=TAVILY_API_KEY
)


# ============================================================
# WEB SEARCH
# ============================================================

@tool
def web_search(query: str) -> str:
    """
    Search the web using Tavily.

    Returns recent search results containing:
    title, URL and content snippet.
    """

    try:
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=False,
            include_raw_content=False
        )

        results = response.get("results", [])

        if not results:
            return "No search results were found."

        output = []

        for index, result in enumerate(results, start=1):

            title = result.get(
                "title",
                "Untitled source"
            )

            url = result.get(
                "url",
                ""
            )

            content = result.get(
                "content",
                ""
            )

            if not url.startswith(("http://", "https://")):
                continue

            output.append(
                f"""
SOURCE {index}

Title:
{title}

URL:
{url}

Snippet:
{content[:800]}
""".strip()
            )

        if not output:
            return "Tavily returned results, but no valid URLs were found."

        return "\n\n" + "\n\n".join(output)

    except Exception as e:

        return (
            f"Web search failed: {type(e).__name__}: {str(e)}"
        )


# ============================================================
# WEBPAGE SCRAPER
# ============================================================

@tool
def scrape_url(url: str) -> str:
    """
    Scrape readable text from a webpage.
    """

    if not url:
        return "ERROR: Empty URL."

    if not url.startswith(("http://", "https://")):
        return (
            f"ERROR: Invalid URL supplied: {url}"
        )

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0 Safari/537.36"
                )
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove unnecessary elements
        for tag in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
                "noscript"
            ]
        ):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        if not text:
            return "ERROR: No readable text found on webpage."

        # Limit content sent to the LLM
        return text[:12000]

    except requests.exceptions.RequestException as e:

        return (
            f"ERROR: Could not scrape URL: {str(e)}"
        )

    except Exception as e:

        return (
            f"ERROR: Unexpected scraping error: "
            f"{type(e).__name__}: {str(e)}"
        )