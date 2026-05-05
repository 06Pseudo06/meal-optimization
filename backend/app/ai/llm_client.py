import requests
import json
import time
import os
from collections import OrderedDict
import concurrent.futures

LLM_CACHE = OrderedDict()
CACHE_MAX_SIZE = 100

BASE_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")

def is_llm_available():
    try:
        requests.get(f"{BASE_URL}/api/tags", timeout=2)
        return True
    except:
        return False

def _make_llm_request(payload: dict) -> dict:
    """Synchronous network request."""
    url = f"{BASE_URL}/api/generate"
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()

def generate_llm_response(query: str, prompt: str) -> str:
    # Check cache first
    if query in LLM_CACHE:
        # Move to end to represent recently used
        LLM_CACHE.move_to_end(query)
        print(json.dumps({"event": "llm_cache_hit", "query": query}))
        return LLM_CACHE[query]

    if not is_llm_available():
        print("llm_skipped")
        return None

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
    
    for attempt in range(2):
        try:
            start_time = time.time()
            
            print("llm_request_sent")
            # Enforce absolute service-level timeout independently of requests timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_make_llm_request, payload)
                data = future.result(timeout=timeout)
            print("llm_response_received")
                
            elapsed = time.time() - start_time
            if elapsed > 5:
                print(json.dumps({"event": "slow_llm_query", "elapsed_seconds": round(elapsed, 2), "query": query}))
                
            result = data.get("response", "")
            
            # Save to cache
            LLM_CACHE[query] = result
            if len(LLM_CACHE) > CACHE_MAX_SIZE:
                LLM_CACHE.popitem(last=False)
                
            print(json.dumps({"event": "llm_success", "attempt": attempt + 1, "query": query}))
            return result
            
        except concurrent.futures.TimeoutError:
            print(json.dumps({"event": "llm_timeout_error", "attempt": attempt + 1, "query": query}))
            if attempt == 1:
                print("llm_failed")
                return None
            time.sleep(2 ** attempt) # Exponential backoff
        except Exception as e:
            print(json.dumps({"event": "llm_request_failed", "attempt": attempt + 1, "error": str(e), "query": query}))
            if attempt == 1:
                print("llm_failed")
                return None
            time.sleep(2 ** attempt) # Exponential backoff

