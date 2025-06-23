import os
from scraper import scrape_chapter
from ai_processing import AIProcessor
from review_interface import ReviewSystem
from version_manager import VersionManager
from retriever import IntelligentRetriever

def run_workflow(api_key, url, human_feedback=None, current_version=None):
    # Initialize components
    processor = AIProcessor(api_key)
    
    # Check if we have valid API
    if not processor.use_gemini:
        print("⚠️ Gemini API not available. Using Hugging Face fallback (lower quality)")
    
    # Scrape content (only if first run)
    if not current_version:
        print("Scraping content...")
        original_content = scrape_chapter(url)
        print("AI spinning content...")
        spun_content = processor.spin_chapter(original_content)
        version = 1
    else:
        # Apply human feedback to existing content
        print("Applying human feedback...")
        results = manager.collection.get(ids=[current_version])
        spun_content = results['documents'][0]
        spun_content = processor.incorporate_feedback(spun_content, human_feedback)
        version = int(current_version.split("_")[1]) + 1
    
    # AI Review
    print("AI reviewing content...")
    ai_feedback = processor.review_content(spun_content)
    
    # Save current version — FIXED LINE: 'contributors' must be a string, not a list
    metadata = {
        "source": url,
        "status": "draft",
        "version": version,
        "contributors": "AI Writer"  # ✅ Fixed: Changed from ["AI Writer"] to "AI Writer"
    }
    version_id = manager.save_version(spun_content, metadata)
    
    # Prepare results
    return {
        "content": spun_content,
        "ai_feedback": ai_feedback,
        "version_id": version_id,
        "version": version
    }