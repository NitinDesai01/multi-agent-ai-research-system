# 🔎 Multi-Agent AI Research System

A sequential multi-agent AI research system where specialized agents handle different stages of the research process instead of using a single LLM for the entire task.

The system searches the web, extracts information from relevant sources, generates a structured research report, and evaluates the final output using a dedicated critic chain.

---

## 🚀 Features

- 🔎 **Search Agent** — Finds recent and relevant web sources using Tavily
- 🌐 **Reader Agent** — Selects and scrapes a relevant source
- ✍️ **Writer Chain** — Generates a structured research report
- 🧐 **Critic Chain** — Reviews and scores the generated report
- 🖥️ **Streamlit UI** — Interactive web interface
- 📥 **Report Download** — Download the generated report
- 🔄 **Sequential Workflow** — Each stage passes its output to the next stage

---

## 🧠 Architecture

```text
User Topic
    │
    ▼
Search Agent
    │
    ▼
Search Results
    │
    ▼
Reader Agent
    │
    ▼
Scraped Research
    │
    ▼
Writer Chain
    │
    ▼
Research Report
    │
    ▼
Critic Chain
    │
    ▼
Report + Feedback
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| LangChain | LLM and agent framework |
| Groq | LLM inference |
| Tavily | Web search |
| BeautifulSoup | Web scraping |
| Streamlit | Web interface |
| python-dotenv | Environment variable management |

---

## 📁 Project Structure

```text
multi-agent-ai-research-system/
│
├── agents.py
├── pipeline.py
├── tools.py
├── app.py
├── test_groq.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### File Responsibilities

- **agents.py** — Contains the AI agents, Writer Chain, and Critic Chain
- **pipeline.py** — Controls the sequential research workflow
- **tools.py** — Contains web search and scraping tools
- **app.py** — Streamlit user interface
- **test_groq.py** — Tests the Groq API connection

---

## 🔄 How It Works

### 1. 🔎 Search Agent

The user enters a research topic.

The Search Agent uses Tavily to find recent and relevant sources.

It returns:

- Source title
- URL
- Relevant snippets

### 2. 🌐 Reader Agent

The Reader Agent receives the search results and selects a relevant source.

It then uses the scraping tool to extract deeper information from the webpage.

### 3. ✍️ Writer Chain

The Writer Chain combines the search results and scraped research to generate a structured report.

The report contains:

- Introduction
- Key findings
- Evidence and examples
- Impact
- Conclusion
- Sources

### 4. 🧐 Critic Chain

The generated report is passed to the Critic Chain.

It evaluates:

- Factual quality
- Clarity
- Completeness
- Evidence
- Organization
- Source quality

The critic then provides a score and improvement suggestions.

---

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/multi-agent-ai-research-system.git
cd multi-agent-ai-research-system
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

> ⚠️ Never upload your `.env` file or expose your API keys publicly.

### 6. Run the Application

```bash
streamlit run app.py
```

The Streamlit application will open in your browser.

---

## 💡 Example

Enter a research topic such as:

```text
Why are companies investing billions in AI despite uncertain returns?
```

The system executes:

```text
Search
  ↓
Find relevant sources
  ↓
Select and scrape a source
  ↓
Generate research report
  ↓
Critically evaluate report
  ↓
Display final results
```

---

## 🎯 Project Goal

The goal of this project is to demonstrate how **Generative AI and Agentic AI workflows** can be used to solve complex research tasks through specialized components.

Instead of:

```text
User → One LLM → Final Answer
```

the system uses:

```text
User
 ↓
Search Agent
 ↓
Reader Agent
 ↓
Writer
 ↓
Critic
 ↓
Final Research
```

This makes the workflow more modular, easier to understand, and easier to extend with additional agents and tools.

---

## 📌 Key Concepts Demonstrated

- Generative AI
- Agentic AI
- Multi-Agent Systems
- LLM Applications
- Tool Calling
- Prompt Engineering
- Web Search
- Web Scraping
- Sequential AI Workflows
- LLM-based Evaluation
- API Integration
- Streamlit Application Development

---

## 🔮 Future Improvements

- [ ] Process multiple sources in parallel
- [ ] Add source reliability scoring
- [ ] Add automatic citation tracking
- [ ] Add fact-checking agent
- [ ] Add RAG-based knowledge retrieval
- [ ] Add PDF report generation
- [ ] Add research history
- [ ] Improve error recovery
- [ ] Add agent observability and tracing

---

## 👨‍💻 Author

**Tanjal Kumar**

Built as a hands-on project focused on:

**Generative AI • Agentic AI • LLM Applications • Multi-Agent Systems**

---

⭐ If you found this project interesting, consider giving the repository a star!
