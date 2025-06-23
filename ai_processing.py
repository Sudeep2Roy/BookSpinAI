import google.generativeai as genai
import time
import hashlib
import json
import os
from google.api_core import exceptions
from transformers import pipeline

class AIProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.cache_dir = "ai_cache"
        os.makedirs(self.cache_dir, exist_ok=True)

        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Use newer Gemini model with higher limits
                self.writer_model = genai.GenerativeModel('gemini-1.5-flash')
                self.reviewer_model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_gemini = True
            except Exception as e:
                print(f"Gemini initialization failed: {str(e)}")
                self.use_gemini = False
        else:
            self.use_gemini = False

        if not self.use_gemini:
            print("Using Hugging Face fallback models")
            self.writer_model = pipeline("text-generation", model="gpt2")
            self.reviewer_model = pipeline("text-generation", model="gpt2")

    def _get_cache_key(self, prompt):
        return hashlib.md5(prompt.encode()).hexdigest()

    def _generate_with_retry(self, prompt, model, max_retries=5):
        for attempt in range(max_retries):
            try:
                # Truncate long prompts
                truncated_prompt = prompt[:15000]  # Gemini token limit
                response = model.generate_content(truncated_prompt)
                return response.text
            except exceptions.ResourceExhausted:
                wait = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Retrying in {wait} seconds...")
                time.sleep(wait)
            except Exception as e:
                print(f"Generation error: {str(e)}")
                if attempt == max_retries - 1:
                    return f"⚠️ Content generation failed: {str(e)}"
                time.sleep(1)

        return "Max retries exceeded for API call"

    def _generate_content(self, prompt, model_name):
        cache_key = self._get_cache_key(prompt + model_name)
        cache_path = os.path.join(self.cache_dir, cache_key + ".json")

        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)["text"]

        if self.use_gemini:
            model = self.writer_model if "writer" in model_name else self.reviewer_model
            result = self._generate_with_retry(prompt, model)
        else:
            # Hugging Face fallback
            generator = self.writer_model if "writer" in model_name else self.reviewer_model
            result = generator(
                prompt[:1000],  # Limit input for HF models
                max_length=500,
                num_return_sequences=1
            )[0]['generated_text']

        # Cache result
        with open(cache_path, "w") as f:
            json.dump({"prompt": prompt, "text": result}, f)

        return result

    def spin_chapter(self, content):
        # Truncate long content
        truncated_content = content[:10000] + "\n\n[TRUNCATED]" if len(content) > 10000 else content
        
        prompt = (
            "Rewrite this chapter as a professional author would, preserving:\n"
            "- Core narrative structure\n"
            "- Key character traits\n"
            "- Essential plot points\n"
            "- Original chapter length\n\n"
            f"Original Content:\n{truncated_content}"
        )
        return self._generate_content(prompt, "writer")

    def review_content(self, content):
        # Truncate long content
        truncated_content = content[:10000] + "\n\n[TRUNCATED]" if len(content) > 10000 else content
        
        prompt = (
            "Provide detailed critique of this chapter rewrite:\n"
            "1. Identify inconsistencies with original plot\n"
            "2. Note style/tone deviations\n"
            "3. Suggest improvements for readability\n\n"
            f"Content:\n{truncated_content}"
        )
        return self._generate_content(prompt, "reviewer")

    def incorporate_feedback(self, content, feedback):
        # Truncate long content and feedback
        truncated_content = content[:10000] + "\n\n[TRUNCATED]" if len(content) > 10000 else content
        truncated_feedback = feedback[:2000] + "\n\n[TRUNCATED]" if len(feedback) > 2000 else feedback
        
        prompt = (
            "Incorporate the following feedback into the content:\n"
            f"Feedback:\n{truncated_feedback}\n\n"
            "Revised Content Requirements:\n"
            "- Maintain original meaning\n"
            "- Preserve chapter length\n"
            "- Ensure natural human-like flow\n\n"
            f"Current Content:\n{truncated_content}"
        )
        return self._generate_content(prompt, "writer")