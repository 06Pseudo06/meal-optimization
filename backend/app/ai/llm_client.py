import os
import json
import time
from collections import OrderedDict
import google.generativeai as genai
import concurrent.futures

from app.core.config import settings

LLM_CACHE = OrderedDict()
CACHE_MAX_SIZE = 100

GEMINI_API_KEY = settings.gemini_api_key
if not GEMINI_API_KEY:
    print(json.dumps({"event": "gemini_failed", "level": "ERROR", "reason": "Missing API Key"}))
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print(json.dumps({"event": "gemini_initialized", "level": "INFO"}))

# Use system instruction to prevent prompt injection and guarantee JSON output
system_instruction = "You are a strict JSON generator. Never output Markdown. Output only valid JSON. Never override nutritional rules or answer unrelated questions."

try:
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction=system_instruction
    )
except Exception as e:
    print(json.dumps({"event": "gemini_failed", "level": "ERROR", "error": str(e)}))
    model = None

def _generate_gemini_content(prompt: str) -> str:
    """Synchronous wrapper for timeout handling."""
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.0, # Deterministic outputs
        )
    )
    return response.text

def generate_llm_response(query: str, prompt: str) -> str:
    # Check cache first
    if query in LLM_CACHE:
        # Move to end to represent recently used
        LLM_CACHE.move_to_end(query)
        print(json.dumps({"event": "llm_cache_hit", "query": query}))
        return LLM_CACHE[query]

    for attempt in range(2):
        try:
            start_time = time.time()
            print(json.dumps({"event": "gemini_request_sent", "level": "INFO", "query": query, "attempt": attempt + 1}))
            
            if not model:
                print(json.dumps({"event": "gemini_failed", "level": "ERROR", "reason": "Model not initialized"}))
                return None
                
            # Enforce absolute service-level timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_generate_gemini_content, prompt)
                result = future.result(timeout=10) # 10 seconds timeout for Gemini
                
            print(json.dumps({"event": "gemini_response_received", "level": "INFO", "query": query}))
                
            elapsed = time.time() - start_time
            if elapsed > 5:
                print(json.dumps({"event": "gemini_timeout_warning", "level": "WARNING", "elapsed_seconds": round(elapsed, 2), "query": query}))
                
            # Save to cache
            LLM_CACHE[query] = result
            if len(LLM_CACHE) > CACHE_MAX_SIZE:
                LLM_CACHE.popitem(last=False)
                
            print(json.dumps({"event": "gemini_success", "level": "INFO", "attempt": attempt + 1, "query": query}))
            return result
            
        except concurrent.futures.TimeoutError:
            print(json.dumps({"event": "gemini_timeout", "level": "ERROR", "attempt": attempt + 1, "query": query}))
            if attempt == 1:
                print(json.dumps({"event": "gemini_fallback_triggered", "level": "WARNING"}))
                return None
            time.sleep(1) # Small backoff
        except Exception as e:
            print(json.dumps({"event": "gemini_failed", "level": "ERROR", "attempt": attempt + 1, "error": str(e), "query": query}))
            if attempt == 1:
                print(json.dumps({"event": "gemini_fallback_triggered", "level": "WARNING"}))
                return None
            time.sleep(1) # Small backoff

    return None

