from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from tools import web_search, scrape_url


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LLM
# ============================================================

# IMPORTANT:
# Keep max_tokens reasonably low because the current Groq
# organization has an 8,000 TPM limit.
#
# The pipeline also limits the amount of research sent
# to each LLM call.

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=1200
)


# ============================================================
# SEARCH AGENT
# ============================================================

def build_search_agent():

    return create_agent(
        model=llm,
        tools=[web_search],

        system_prompt="""
You are the Search Agent in a multi-agent research system.

Your ONLY responsibility is web searching.

TASK:
Find recent and reliable sources for the user's research topic.

RULES:

1. Call the web_search tool exactly ONE time.
2. Do not call the tool more than once.
3. Do not write a research report.
4. Do not summarize the entire topic.
5. Do not invent sources.
6. Do not invent URLs.
7. Return the search tool results with minimal modification.
8. Do not create tables.

The web_search tool already returns:
- source titles
- URLs
- snippets

After the tool call, return the useful search results.
"""
    )


# ============================================================
# READER AGENT
# ============================================================

def build_reader_agent():

    return create_agent(
        model=llm,
        tools=[],

        system_prompt="""
You are the Reader Agent in a multi-agent research system.

Your responsibility is to analyze webpage content that has
ALREADY been scraped by the pipeline.

You DO NOT need to search the web.

You DO NOT need to call any tools.

Analyze ONLY the supplied source content.

Extract:

1. The most important facts.
2. Important statistics.
3. Important examples.
4. Major findings.
5. Limitations or caveats.
6. Why the source is relevant to the research topic.

IMPORTANT RULES:

- Use ONLY information present in the supplied content.
- Never invent statistics.
- Never invent facts.
- Never invent URLs.
- Do not make assumptions that are not supported by the source.
- If the webpage contains an error or insufficient information,
  clearly state that.
- Keep the response concise.
- Do not create tables.

Return exactly this structure:

SOURCE SUMMARY:
<2-3 sentence summary>

KEY FINDINGS:
- Finding
- Finding
- Finding

IMPORTANT STATISTICS:
- Statistic and explanation
- Statistic and explanation

EXAMPLES:
- Example
- Example

LIMITATIONS:
- Limitation
- Limitation

RELEVANCE:
<Why this source is useful for the research topic>
"""
    )


# ============================================================
# WRITER CHAIN
# ============================================================

writer_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
You are the Writer Agent in a multi-agent AI research system.

Your task is to create a factual and professional research report
using ONLY the research evidence supplied to you.

IMPORTANT RULES:

1. Use only the supplied research.
2. Do not invent facts.
3. Do not invent statistics.
4. Do not invent examples.
5. Do not invent sources.
6. Do not invent URLs.
7. Do not make unsupported claims.
8. Clearly mention limitations when evidence is limited.
9. Do NOT create Markdown tables.
10. Use headings, paragraphs and bullet points instead.
11. Keep paragraphs short.
12. Avoid unnecessary repetition.
13. Distinguish documented findings from possible implications.
14. Do not claim that a source proves something unless the supplied
    evidence actually supports it.

The report should be readable by a university student or researcher.
"""
    ),

    (
        "human",
        """
Write a research report about:

Topic:
{topic}

Research Evidence:
{research}

Use EXACTLY this structure:

# Research Report: {topic}

## 1. Introduction

Explain the topic and why it is important.

## 2. Key Findings

### Finding 1

Explain the first major finding using available evidence.

### Finding 2

Explain the second major finding using available evidence.

### Finding 3

Explain the third major finding using available evidence.

### Finding 4

Include a fourth finding only if sufficient evidence exists.

## 3. Evidence and Examples

Present important evidence, statistics and examples.

Use bullet points.

DO NOT create a table.

## 4. Impact

Explain the demonstrated impact supported by the evidence.

Then explain possible future implications separately if appropriate.

Do not present speculation as fact.

## 5. Limitations

Clearly explain limitations such as:

- limited sources
- geographic limitations
- unavailable webpages
- lack of independent verification
- lack of outcome data
- insufficient evidence

Only include limitations relevant to the supplied research.

## 6. Conclusion

Give a concise conclusion based only on the evidence.

## 7. Sources

List the source title and URL for each source used.

IMPORTANT:

DO NOT CREATE A MARKDOWN TABLE.

DO NOT INVENT INFORMATION.

DO NOT INVENT STATISTICS.

DO NOT INVENT URLS.

DO NOT ADD SOURCES THAT WERE NOT PROVIDED.
"""
    )

])


writer_chain = (
    writer_prompt
    | llm
    | StrOutputParser()
)


# ============================================================
# CRITIC CHAIN
# ============================================================

critic_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
You are the Critic Agent in a multi-agent research system.

Your job is to critically evaluate the final research report.

Evaluate:

- factual reliability
- evidence quality
- source quality
- completeness
- clarity
- organization
- unsupported claims
- use of statistics
- limitations
- consistency with the supplied evidence

Be strict but constructive.

IMPORTANT:

Do not rewrite the report.

Do not invent facts.

Do not create a table.

Give practical recommendations for improvement.
"""
    ),

    (
        "human",
        """
Evaluate this research report.

Topic:
{topic}

Report:
{report}

Respond exactly using this structure:

Score: X/10

Factual Quality: X/10
Evidence Quality: X/10
Source Quality: X/10
Completeness: X/10
Clarity: X/10

Strengths:
- ...
- ...
- ...

Areas to Improve:
- ...
- ...
- ...

Major Evidence Problem:
...

Recommended Improvement:
...

One line verdict:
...
"""
    )

])


critic_chain = (
    critic_prompt
    | llm
    | StrOutputParser()
)
