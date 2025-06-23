# BookSpinAI
An AI-powered book processing workflow using Google Gemini, Streamlit, and ChromaDB with human-in-the-loop editing, quality checks, and versioned search.
# 📘 Automated Book Publication Workflow

A streamlined AI-powered system to fetch, rewrite, review, and finalize book chapters from the web using Google Gemini, Streamlit, and ChromaDB.

## 🚀 Features

- ✅ Web scraping with screenshots (Playwright)
- ✅ AI content rewriting & reviewing (Gemini API)
- ✅ Human-in-the-loop feedback loop
- ✅ ChromaDB versioning and intelligent retrieval
- ✅ Streamlit dashboard with quality checks and system metrics

## 📂 Project Structure

- `app2.py` – Main Streamlit application
- `scrape_and_save.py` – Scrapes HTML and saves screenshots
- `chapter_raw.html` – Sample fetched chapter
- `.gitignore` – Ignores envs, cache, screenshots, etc.

## 🛠️ Setup

```bash
git clone https://github.com/your-username/book-publication-workflow.git
cd book-publication-workflow
pip install -r requirements.txt
playwright install
# Automated Book Publication Workflow

## Setup
```bash
pip install -r requirements.txt
playwright install
First run:python scrap_and_save.py
then streamlit run app.py
