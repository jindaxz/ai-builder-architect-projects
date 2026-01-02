"""
Flask Server
Now serves both the JSON API and a simple web UI that talks to Ollama.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
from typing import List, Dict
from ollama_client import OllamaClient
from config import SERVER_HOST, SERVER_PORT, DEBUG, ALLOWED_ORIGINS

app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS)

ollama = OllamaClient()


DEMO_RESULTS: List[Dict[str, str]] = [
    {
        "title": "Quantum Computing Breakthroughs Explained",
        "url": "https://example.com/quantum-breakthroughs",
        "snippet": (
            "A research roundup describing the most notable advances in quantum computing over the past year, "
            "including improved qubit stability, expanded error correction, and new demonstrations of quantum "
            "advantage for scientific simulations. Tailored for the query \"{query}\"."
        )
    },
    {
        "title": "Industry Impact of Recent Quantum Milestones",
        "url": "https://example.com/industry-impact",
        "snippet": (
            "Covers how hyperscalers and startups are productizing the latest discoveries, with practical notes "
            "on what the \"{query}\" topic means for cloud APIs, post-quantum cryptography, and hardware roadmaps."
        )
    },
    {
        "title": "Academic Papers to Watch",
        "url": "https://example.com/academic-tracker",
        "snippet": (
            "A curated watch list of peer-reviewed papers aligned with \"{query}\". Includes summaries of "
            "breakthroughs in topological qubits, neutral-atom arrays, and benchmarking research."
        )
    },
    {
        "title": "What Comes Next in Quantum",
        "url": "https://example.com/future-outlook",
        "snippet": (
            "Forward-looking analysis outlining expected milestones for 2026–2028, plus the key open challenges "
            "researchers must solve to fully realize the promise of \"{query}\"."
        )
    }
]


def get_demo_results(query: str) -> List[Dict[str, str]]:
    """Return a static set of results for demo purposes."""
    return [
        {
            "title": item["title"],
            "url": item["url"],
            "snippet": item["snippet"].format(query=query)
        }
        for item in DEMO_RESULTS
    ]


@app.route('/', methods=['GET'])
def home():
    """Serve the simple search UI"""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Search Enhancer"
    })


@app.route('/ollama/status', methods=['GET'])
def ollama_status():
    """Check Ollama connection status"""
    status = ollama.test_connection()
    return jsonify(status)


@app.route('/summarize', methods=['POST'])
def summarize():
    """Summarize search results"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        query = data.get('query', '')
        results = data.get('results', [])

        if not query:
            return jsonify({
                "success": False,
                "error": "Query is required"
            }), 400

        if not results:
            return jsonify({
                "success": False,
                "error": "No results provided"
            }), 400

        if not ollama.check_health():
            return jsonify({
                "success": False,
                "error": "Ollama is not running. Please start Ollama with 'ollama serve'"
            }), 503

        result = ollama.summarize_search_results(query, results)

        return jsonify(result)

    except Exception as e:
        print(f"Error in summarize endpoint: {e}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/search', methods=['POST'])
def search():
    """Full search flow: scrape Google and generate Ollama summary"""
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()

        if not query:
            return jsonify({
                "success": False,
                "error": "Query is required"
            }), 400

        results = get_demo_results(query)

        if not ollama.check_health():
            return jsonify({
                "success": False,
                "error": "Ollama is not running. Please start Ollama with 'ollama serve'"
            }), 503

        summary = ollama.summarize_search_results(query, results)
        summary["results"] = results
        return jsonify(summary)

    except Exception as e:
        print(f"Error in search endpoint: {e}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/models', methods=['GET'])
def list_models():
    """List available Ollama models"""
    models = ollama.list_models()
    return jsonify({
        "models": models,
        "current": ollama.model
    })


@app.route('/test', methods=['POST'])
def test_summary():
    """Test endpoint with sample data"""
    sample_results = [
        {
            "title": "Artificial Intelligence - Wikipedia",
            "snippet": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans.",
            "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
        },
        {
            "title": "What is AI? Artificial Intelligence Explained",
            "snippet": "AI enables computers and machines to simulate human intelligence and problem-solving capabilities.",
            "url": "https://www.ibm.com/topics/artificial-intelligence"
        }
    ]

    result = ollama.summarize_search_results(
        "what is artificial intelligence",
        sample_results
    )

    return jsonify(result)


if __name__ == '__main__':
    print(f"🚀 Starting AI Search Enhancer Server...")
    print(f"📍 Server: http://{SERVER_HOST}:{SERVER_PORT}")

    print(f"\n🤖 Checking Ollama connection...")
    status = ollama.test_connection()

    if status['connected']:
        print(f"✅ Ollama connected: {status['host']}")
        print(f"✅ Model: {status['model']}")
        if status.get('available_models'):
            print(f"📚 Available models: {', '.join(status['available_models'][:3])}...")
    else:
        print(f"❌ Ollama not connected: {status.get('error')}")
        print(f"💡 Make sure Ollama is running: ollama serve")

    print(f"\n🌐 CORS enabled for: {ALLOWED_ORIGINS}")
    print(f"🔧 Debug mode: {DEBUG}")
    print(f"\n✨ Server ready! Open http://{SERVER_HOST}:{SERVER_PORT} to use the built-in search UI.\n")

    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=DEBUG
    )
