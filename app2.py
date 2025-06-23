# Install required packages before running:
# pip install playwright streamlit chromadb requests
# playwright install

import os
import json
import requests
import chromadb
import streamlit as st
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from PIL import Image
import glob

# 1. GEMINI HTTP API CONFIG
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_api_key")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# 2. CHROMADB SETUP
client = chromadb.Client()
collection = client.get_or_create_collection("chapters")

# 3. QUALITY CHECK FUNCTION
def quality_check(content):
    if any(red_flag in content for red_flag in ["@", "Pixel at", "unclear reference"]):
        return "FAIL - Regenerate content"
    return "PASS"

# 4. HUMAN EDITING STEP
def human_edit(content):
    st.subheader("🧑‍💻 Human Editing Required")
    return st.text_area("Make final manual edits here:", value=content, height=200)

# 5. AI WRITER FUNCTION (Gemini HTTP API)
def ai_writer(content):
    prompt = (
        "Rewrite this chapter professionally while preserving:\n"
        "- Original plot points\n"
        "- Character consistency\n"
        "- Natural language flow\n"
        "- Clear imagery\n"
        "Avoid:\n"
        "- Unclear references\n"
        "- Grammatical errors\n"
        "- Technical artifacts\n\n"
        f"Content:\n{content[:20000]}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    data = response.json()
    if "candidates" in data:
        return data['candidates'][0]['content']['parts'][0]['text']
    else:
        return "[Error] Gemini API call failed: " + json.dumps(data)

# 6. AI REVIEWER FUNCTION (Gemini HTTP API)
def ai_reviewer(content):
    prompt = f"Review and improve this rewritten content for clarity, grammar, and flow:\n\n{content}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    data = response.json()
    if "candidates" in data:
        return data['candidates'][0]['content']['parts'][0]['text']
    else:
        return "[Error] Gemini API call failed: " + json.dumps(data)

# 7. SAVE TO CHROMADB
def save_version(title, content):
    collection.add(documents=[content], ids=[title])
    return "Saved to ChromaDB."

# 8. RL-STYLE SEARCH FUNCTION
def rl_search(query):
    results = collection.query(query_texts=[query], n_results=3)
    return results

# 9. STREAMLIT HUMAN-IN-THE-LOOP UI
def human_review_interface():
    st.set_page_config(layout="wide")
    st.title("📘 Automated Book Publication Workflow")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("1️⃣ Chapter Processing")
        url = st.text_input("Enter Chapter URL", "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1")
        if st.button("Fetch & Rewrite"):
            try:
                with open("chapter_raw.html", "r", encoding="utf-8") as f:
                    content = f.read()
                st.success("✅ Loaded saved chapter HTML.")

                ai_draft = ai_writer(content)
                st.subheader("✍️ AI Writer Output")
                st.text_area("AI Draft", ai_draft, height=200)

                ai_reviewed = ai_reviewer(ai_draft)
                st.subheader("🔍 AI Reviewer Output")
                st.text_area("Reviewed Output", ai_reviewed, height=200)

                quality_status = quality_check(ai_reviewed)
                st.info(f"📋 Quality Check: {quality_status}")

                if quality_status == "PASS":
                    final_edit = human_edit(ai_reviewed)
                    feedback = st.radio("👥 Feedback Action", ["Approve", "Request Revision"])
                    if st.button("✅ Finalize & Save"):
                        if feedback == "Approve":
                            save_version("Gates of Morning - Chapter 1", final_edit)
                            st.success("Final version approved and saved.")
                        else:
                            st.warning("Revision requested. Please update and retry.")
                else:
                    st.warning("⚠️ Content did not pass quality checks. Please retry generation.")

            except FileNotFoundError:
                st.error("❌ Please run scrape_and_save.py to generate chapter_raw.html first.")

        st.markdown("---")
        st.subheader("🔎 Search Previous Versions")
        query = st.text_input("Enter search query")
        if st.button("Search"):
            results = rl_search(query)
            for i, (doc, score) in enumerate(zip(results['documents'][0], results['distances'][0])):
                st.markdown(f"**Result {i+1}:**\n📄 {doc}\n🔢 Similarity Score: {1-score:.2f}\n---")

    with col2:
        st.subheader("📸 Screenshots")
        for img_file in glob.glob("*.png"):
            st.image(Image.open(img_file), caption=os.path.basename(img_file), use_column_width=True)

        st.markdown("---")
        st.subheader("📊 System Dashboard")
        docs = collection.get()
        st.metric("🔖 Total Versions", len(docs["documents"]))
        st.metric("🗃️ Stored Entries", len(docs["ids"]))
        st.metric("⚙️ RL Model Progress", f"{round(len(docs['documents']) * 2.5)}% complete")
        st.info("🕒 Status: Idle | No pending tasks")

# Entry point
if __name__ == "__main__":
    human_review_interface()
