"""
Configuration for AI Search Enhancer
"""

import os

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Server Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")

# Search Configuration
MAX_RESULTS = 10
MAX_RESULT_LENGTH = 300

# AI Configuration
SUMMARY_MAX_TOKENS = 500
TEMPERATURE = 0.3

# CORS Configuration
ALLOWED_ORIGINS = ["*"]

# Prompts
SYSTEM_PROMPT = """You are a helpful AI assistant that summarizes web search results.
Your task is to analyze search results and provide a concise, informative summary.

Guidelines:
- Be concise and factual
- Highlight the most relevant information
- Organize information logically
- Use bullet points when appropriate
- Cite key findings from the results
- Keep the summary under 300 words
"""

SUMMARY_PROMPT_TEMPLATE = """Based on these search results for the query "{query}", provide a comprehensive summary:

Search Results:
{results}

Please provide:
1. A brief overview (2-3 sentences)
2. Key findings or main points (3-5 bullet points)
3. Any important nuances or caveats

Summary:"""
