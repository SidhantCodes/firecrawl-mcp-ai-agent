# 🧠 Developer Tools Research Agent

A smart research agent that analyzes and compares developer tools based on real web data, LLM-driven analysis, and concise recommendations.

## 🚀 Features

* 🔍 **Web Search & Scraping**: Finds and scrapes relevant articles and tool pages using the Firecrawl API.
* 🤖 **LLM Analysis**: Uses structured LLM prompts to extract and summarize developer-relevant insights like pricing models, tech stack, APIs, and integrations.
* 📊 **Tool Comparison**: Compares tools for developer use cases and generates concise recommendations.
* 🛠️ **Modular Workflow**: Built with LangGraph for clean and extensible step-by-step analysis.

## 📦 Structure

```
├── main.py               # CLI entry point
src/
├── firecrawl.py          # Web scraping and search using Firecrawl
├── workflow.py           # Main research and analysis pipeline
├── models.py             # Pydantic models for structured data
├── prompts.py            # LLM prompt templates
```

## 🧪 Example Use

```bash
python main.py
🔍 Developer Tools Query: firebase alternatives
```

Outputs a comparison of 3–4 tools, with details like:

* Website, pricing model, open-source status
* Supported languages and integrations
* Technical description and a final recommendation

## 🔐 Environment Variables

Make sure to set the following in your `.env` file:

```
FIRECRAWL_API_KEY=your_firecrawl_api_key
GOOGLE_API_KEY=your_google_api_key
```

## 📚 Dependencies

* Python 3.9+
* `firecrawl`, `langgraph`, `langchain`, `pydantic`, `python-dotenv`
