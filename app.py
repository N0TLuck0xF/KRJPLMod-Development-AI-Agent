import openai
import requests
import os
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Secure API Key retrieval from environment variables
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROKAI_API_KEY = os.getenv("GROKAI_API_KEY")
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")

executor = ThreadPoolExecutor(max_workers=4)

def query_api(url, headers, payload, ai_name):
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10).json()
        return {ai_name: response.get("message") or response.get("completion") or response.get("response", "Error fetching response")}
    except Exception as e:
        return {ai_name: str(e)}

def query_all_apis(prompt):
    tasks = [
        executor.submit(query_api, "https://api.anthropic.com/v1/messages", {"Authorization": f"Bearer {CLAUDE_API_KEY}"}, {"model": "claude-v1", "prompt": prompt}, "Claude"),
        executor.submit(query_api, "https://api.deepseek.com/v1/generate", {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, {"prompt": prompt}, "DeepSeekAI"),
        executor.submit(query_api, "https://api.grokai.com/v1/chat", {"Authorization": f"Bearer {GROKAI_API_KEY}"}, {"prompt": prompt}, "GrokAI"),
        executor.submit(query_api, "https://api.openai.com/v1/chat/completions", {"Authorization": f"Bearer {CHATGPT_API_KEY}"}, {"model": "gpt-4", "messages": [{"role": "system", "content": prompt}]}, "ChatGPT")
    ]
    results = {}
    for task in tasks:
        results.update(task.result())
    return results

@app.route("/generate", methods=["POST"])
def generate_language_component():
    data = request.json
    prompt = data.get("prompt", "Define a new programming language structure.")
    responses = query_all_apis(prompt)
    return jsonify(responses)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
