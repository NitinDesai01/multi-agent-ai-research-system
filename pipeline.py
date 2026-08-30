import re
from urllib.parse import urlparse

from agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_SOURCES = 3

# Maximum amount of scraped text used for each Reader call.
# This prevents large webpages from consuming too many tokens.
MAX_SCRAPED_CHARS = 5000

# Maximum amount of reader output passed to the Writer.
MAX_READER_CHARS = 2500

# Maximum amount of combined research passed to Writer.
MAX_RESEARCH_CHARS = 7500


# ============================================================
# URL VALIDATION
# ============================================================

def is_valid_url(url: str) -> bool:

    if not isinstance(url, str):
        return False

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        return False

    try:

        parsed = urlparse(url)

        return bool(
            parsed.scheme
            and parsed.netloc
        )

    except Exception:

        return False


# ============================================================
# EXTRACT URLS
# ============================================================

def extract_urls(text: str) -> list[str]:

    if not text:
        return []

    candidates = re.findall(
        r'https?://[^\s<>"\]\)]+',
        text
    )

    urls = []

    for url in candidates:

        url = url.rstrip(
            ".,;:!?)]}'\""
        )

        if (
            is_valid_url(url)
            and url not in urls
        ):

            urls.append(url)

    return urls


# ============================================================
# PARSE TAVILY SOURCES
# ============================================================

def parse_sources(search_text: str) -> list[dict]:

    if not search_text:
        return []

    sources = []

    # --------------------------------------------------------
    # Format produced by tools.py
    #
    # SOURCE 1
    #
    # Title: ...
    # URL: ...
    # Snippet: ...
    # --------------------------------------------------------

    blocks = re.split(
        r'\n\s*SOURCE\s+\d+\s*\n',
        search_text,
        flags=re.IGNORECASE
    )

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title_match = re.search(
            r'Title:\s*(.*?)\s*\n\s*URL:',
            block,
            flags=re.DOTALL | re.IGNORECASE
        )

        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        url_match = re.search(
            r'URL:\s*(https?://[^\s]+)',
            block,
            flags=re.IGNORECASE
        )

        # ----------------------------------------------------
        # SNIPPET
        # ----------------------------------------------------

        snippet_match = re.search(
            r'(?:Snippet|snippets):\s*(.*)',
            block,
            flags=re.DOTALL | re.IGNORECASE
        )

        if not url_match:
            continue

        url = url_match.group(1).strip()

        url = url.rstrip(
            ".,;:!?)]}'\""
        )

        if not is_valid_url(url):
            continue

        if title_match:

            title = title_match.group(1).strip()

        else:

            title = "Untitled source"

        if snippet_match:

            snippet = snippet_match.group(1).strip()

        else:

            snippet = ""

        sources.append({
            "title": title,
            "url": url,
            "snippet": snippet
        })

    # --------------------------------------------------------
    # Remove duplicate URLs
    # --------------------------------------------------------

    unique_sources = []
    seen_urls = set()

    for source in sources:

        url = source["url"]

        if url not in seen_urls:

            seen_urls.add(url)

            unique_sources.append(source)

    return unique_sources


# ============================================================
# CLEAN SCRAPED CONTENT
# ============================================================

def clean_scraped_content(content: str) -> str:

    if not content:
        return ""

    content = str(content)

    # Remove excessive whitespace
    content = re.sub(
        r'\s+',
        ' ',
        content
    )

    return content.strip()


# ============================================================
# RESEARCH PIPELINE
# ============================================================

def run_research_pipeline(
    topic: str,
    progress_callback=None
) -> dict:

    state = {}

    # ========================================================
    # PROGRESS HELPER
    # ========================================================

    def progress(message):

        if progress_callback:

            progress_callback(message)

        else:

            print(message)

    # ========================================================
    # VALIDATE TOPIC
    # ========================================================

    if not topic or not topic.strip():

        raise ValueError(
            "Research topic cannot be empty."
        )

    topic = topic.strip()

    # ========================================================
    # STEP 1 — SEARCH AGENT
    # ========================================================

    progress(
        "Step 1 — Search Agent is searching the web..."
    )

    search_agent = build_search_agent()

    search_result = search_agent.invoke({

        "messages": [

            (
                "user",

                f"""
Research this topic:

{topic}

Use the web_search tool exactly once.

Find recent and reliable sources.
"""
            )

        ]

    })

    # ========================================================
    # GET SEARCH MESSAGES
    # ========================================================

    search_messages = search_result.get(
        "messages",
        []
    )

    # ========================================================
    # GET ACTUAL TOOL RESPONSE
    # ========================================================

    search_tool_messages = [

        message

        for message in search_messages

        if getattr(
            message,
            "type",
            ""
        ) == "tool"

    ]

    if search_tool_messages:

        search_text = str(
            search_tool_messages[-1].content
        )

    elif search_messages:

        search_text = str(
            search_messages[-1].content
        )

    else:

        raise RuntimeError(
            "Search Agent returned no results."
        )

    if not search_text.strip():

        raise RuntimeError(
            "Search Agent returned empty results."
        )

    state["search_results"] = search_text

    # ========================================================
    # PARSE SOURCES
    # ========================================================

    sources = parse_sources(
        search_text
    )

    # ========================================================
    # FALLBACK URL EXTRACTION
    # ========================================================

    if not sources:

        urls = extract_urls(
            search_text
        )

        sources = [

            {
                "title": "Search Result",
                "url": url,
                "snippet": ""
            }

            for url in urls
        ]

    if not sources:

        raise RuntimeError(
            "No valid HTTP/HTTPS URLs were found."
        )

    progress(
        f"Step 1 completed — {len(sources)} valid sources found."
    )

    # ========================================================
    # STEP 2 — READER AGENT
    # ========================================================

    progress(
        "Step 2 — Reader Agent is reading the most relevant sources..."
    )

    reader_agent = build_reader_agent()

    # --------------------------------------------------------
    # Import scraper
    # --------------------------------------------------------

    from tools import scrape_url

    scraped_sources = []

    reader_summaries = []

    # ========================================================
    # TRY UP TO 3 SOURCES
    # ========================================================

    for index, source in enumerate(
        sources[:MAX_SOURCES],
        start=1
    ):

        title = source["title"]

        url = source["url"]

        progress(
            f"Reading source {index}/{min(MAX_SOURCES, len(sources))}: {title}"
        )

        # ====================================================
        # SCRAPE SOURCE
        # ====================================================

        try:

            scraped_result = scrape_url.invoke({
                "url": url
            })

            scraped_result = clean_scraped_content(
                scraped_result
            )

        except Exception as e:

            scraped_result = (
                f"ERROR: Could not scrape URL: {str(e)}"
            )

        # ====================================================
        # DETECT FAILED SCRAPE
        # ====================================================

        failed_scrape = (

            not scraped_result

            or scraped_result.startswith(
                "ERROR:"
            )

            or scraped_result.startswith(
                "Could not scrape"
            )

        )

        # ----------------------------------------------------
        # Save scraped source information
        # ----------------------------------------------------

        scraped_sources.append({

            "title": title,

            "url": url,

            "content": scraped_result

        })

        # ====================================================
        # SKIP FAILED SOURCE
        # ====================================================

        if failed_scrape:

            progress(
                f"Skipped source {index} — webpage could not be scraped."
            )

            continue

        # ====================================================
        # LIMIT CONTENT SIZE
        # ====================================================

        limited_content = (
            scraped_result[
                :MAX_SCRAPED_CHARS
            ]
        )

        # ====================================================
        # READER INPUT
        # ====================================================

        reader_input = f"""
Research topic:

{topic}

Source title:

{title}

Verified source URL:

{url}

Scraped webpage content:

{limited_content}

Analyze this source using only the content above.
"""

        # ====================================================
        # CALL READER
        # ====================================================

        try:

            reader_result = reader_agent.invoke({

                "messages": [

                    (
                        "user",
                        reader_input
                    )

                ]

            })

            reader_messages = reader_result.get(
                "messages",
                []
            )

            if reader_messages:

                reader_summary = str(
                    reader_messages[-1].content
                )

            else:

                reader_summary = (
                    "Reader Agent returned no summary."
                )

        except Exception as e:

            progress(
                f"Reader Agent failed for source {index}."
            )

            reader_summary = (
                f"Reader Agent error: {str(e)}"
            )

        # ====================================================
        # LIMIT READER OUTPUT
        # ====================================================

        reader_summary = reader_summary[
            :MAX_READER_CHARS
        ]

        reader_summaries.append({

            "title": title,

            "url": url,

            "summary": reader_summary

        })

    # ========================================================
    # CHECK SUCCESSFUL SOURCES
    # ========================================================

    if not reader_summaries:

        raise RuntimeError(
            "None of the selected webpages could be successfully read."
        )

    progress(
        f"Step 2 completed — {len(reader_summaries)} sources successfully analyzed."
    )

    # ========================================================
    # COMBINE RESEARCH
    # ========================================================

    research_parts = []

    for item in reader_summaries:

        research_parts.append(

            f"""
SOURCE TITLE:
{item["title"]}

SOURCE URL:
{item["url"]}

READER ANALYSIS:
{item["summary"]}
""".strip()

        )

    research_combined = (

        "\n\n--------------------\n\n"

        + "\n\n".join(
            research_parts
        )

    )

    # ========================================================
    # FINAL RESEARCH LIMIT
    # ========================================================

    research_combined = (
        research_combined[
            :MAX_RESEARCH_CHARS
        ]
    )

    state["research_combined"] = research_combined

    # ========================================================
    # STEP 3 — WRITER
    # ========================================================

    progress(
        "Step 3 — Writer is creating the research report..."
    )

    try:

        report = writer_chain.invoke({

            "topic": topic,

            "research": research_combined

        })

    except Exception as e:

        raise RuntimeError(
            f"Writer Agent failed: {str(e)}"
        )

    if not report:

        raise RuntimeError(
            "Writer failed to generate a report."
        )

    report = str(report)

    state["report"] = report

    progress(
        "Step 3 completed."
    )

    # ========================================================
    # STEP 4 — CRITIC
    # ========================================================

    progress(
        "Step 4 — Critic is evaluating research quality..."
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Critic receives ONLY the final report.
    #
    # We do NOT send the complete scraped research again.
    #
    # This prevents the previous Groq 413 TPM problem.
    # --------------------------------------------------------

    try:

        critic = critic_chain.invoke({

            "topic": topic,

            "report": report

        })

    except Exception as e:

        # Do not destroy the complete research result if
        # the critic fails.

        critic = (
            f"Critic Agent could not evaluate the report: {str(e)}"
        )

        progress(
            "Warning — Critic Agent failed, but the research report was generated."
        )

    state["critic"] = critic

    progress(
        "Step 4 completed."
    )

    # ========================================================
    # FINAL STATE
    # ========================================================

    state["sources"] = sources

    state["scraped_sources"] = scraped_sources

    state["reader_summaries"] = reader_summaries

    return state
