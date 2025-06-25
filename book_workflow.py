# Install required packages before running:
# pip install playwright streamlit chromadb google-generativeai
# playwright install

import os
import chromadb
import streamlit as st
from playwright.sync_api import sync_playwright
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import google.generativeai as genai

# 1. SETUP GEMINI API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_api_key")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# 2. CHROMADB SETUP
client = chromadb.Client()
collection = client.get_or_create_collection("chapters")

# 3. SCRAPE AND SCREENSHOT FUNCTION
def fetch_chapter_and_screenshot(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path="screenshot.png", full_page=True)
        content = page.inner_html("div#bodyContent")
        browser.close()
    return content

# 4. AI WRITER FUNCTION
def ai_writer(content):
    prompt = f"Rewrite the following in modern, clear, and engaging English:\n\n{content}"
    response = model.generate_content(prompt)
    return response.text

# 5. AI REVIEWER FUNCTION
def ai_reviewer(content):
    prompt = f"Review and improve this rewritten content for clarity, grammar, and flow:\n\n{content}"
    response = model.generate_content(prompt)
    return response.text

# 6. SAVE TO CHROMADB
def save_version(title, content):
    collection.add(documents=[content], ids=[title])
    return "Saved to ChromaDB."

# 7. RL-STYLE SEARCH FUNCTION
def rl_search(query):
    results = collection.query(query_texts=[query], n_results=3)
    return results

# 8. STREAMLIT HUMAN-IN-THE-LOOP UI
def human_review_interface():
    st.title("Automated Book Publication Workflow")

    url = st.text_input("Enter Chapter URL", "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1")
    if st.button("Fetch & Rewrite"):
        content = fetch_chapter_and_screenshot(url)
        st.success("Scraped successfully.")

        ai_draft = ai_writer(content)
        st.subheader("✍️ AI Writer Output")
        st.text_area("AI Draft", ai_draft, height=300)

        ai_reviewed = ai_reviewer(ai_draft)
        st.subheader("🔍 AI Reviewer Output")
        edited = st.text_area("Edit (Optional)", ai_reviewed, height=300)

        if st.button("✅ Finalize & Save"):
            save_version("Gates of Morning - Chapter 1", edited)
            st.success("Final version saved.")

    st.markdown("---")
    st.subheader("🔎 Search Previous Versions")
    query = st.text_input("Enter search query")
    if st.button("Search"):
        results = rl_search(query)
        for i, doc in enumerate(results['documents'][0]):
            st.markdown(f"**Result {i+1}:**\n{doc}\n---")

# Entry point
if __name__ == "__main__":
    human_review_interface()
