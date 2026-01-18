#!/usr/bin/env python3
"""
Cline Integration for Elixir RAG System
Provides Ollama-compatible API endpoints for context-aware code assistance
"""
from flask import Flask, request, jsonify
from rag_system import ElixirRAG
from vector_db import CodeVectorDB
from embeddings import HybridCodeEmbedder
import os
import logging
import traceback
import sys
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('cline_integration.log')
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Flask to handle JSON responses properly
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Global RAG system (lazy loading)
rag_system = None

def get_rag_system():
    """Initialize RAG system on first use"""
    global rag_system
    if rag_system is None:
        logger.info("🔧 Initializing RAG system...")
        try:
            logger.debug("Creating CodeVectorDB...")
            db = CodeVectorDB()
            logger.debug("CodeVectorDB created successfully")

            logger.debug("Creating HybridCodeEmbedder...")
            embedder = HybridCodeEmbedder()
            logger.debug("HybridCodeEmbedder created successfully")

            model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
            logger.debug(f"Using model: {model_name}")

            logger.debug("Creating ElixirRAG system...")
            rag_system = ElixirRAG(
                vector_db=db,
                embedder=embedder,
                model=model_name
            )
            logger.info("✅ RAG system ready!")

            # Log database stats
            try:
                stats = rag_system.db.get_stats()
                logger.info(f"Database stats: {stats}")
            except Exception as e:
                logger.warning(f"Could not get database stats: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG system: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    return rag_system

@app.route('/health', methods=['GET'])
def health_check():
    """Check if system is ready"""
    logger.info("🔍 Health check requested")
    try:
        rag = get_rag_system()
        stats = rag.db.get_stats()
        logger.info(f"Health check successful: {stats}")
        response = jsonify({
            'status': 'ready',
            'model': os.getenv('OLLAMA_MODEL', 'llama3.2:3b'),
            'database_stats': stats
        })
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_response = jsonify({
            'status': 'error',
            'error': str(e)
        })
        error_response.headers['Content-Type'] = 'application/json'
        return error_response, 500

@app.route('/api/tags', methods=['GET'])
def ollama_tags():
    """Ollama-compatible endpoint for model listing"""
    logger.info("🏷️ Model tags requested")
    try:
        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        logger.debug(f"Returning model: {model_name}")

        response_data = {
            "models": [
                {
                    "name": model_name,
                    "model": model_name,
                    "modified_at": "2024-01-01T00:00:00Z",
                    "size": 2000000000,
                    "digest": "sha256:fake"
                }
            ]
        }

        response = jsonify(response_data)
        response.headers['Content-Type'] = 'application/json'
        logger.debug("Model tags response sent successfully")
        return response

    except Exception as e:
        logger.error(f"❌ Model tags endpoint failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_response = jsonify({'error': str(e)})
        error_response.headers['Content-Type'] = 'application/json'
        return error_response, 500

@app.route('/api/chat', methods=['POST'])
def ollama_chat():
    """Ollama-compatible chat endpoint for Cline"""
    logger.info("💬 Chat endpoint requested")
    try:
        data = request.json
        logger.debug(f"Request data: {data}")

        messages = data.get('messages', [])
        logger.debug(f"Messages received: {len(messages)} messages")

        if not messages:
            logger.warning("No messages provided in request")
            return jsonify({'error': 'Messages are required'}), 400

        # Get the last user message
        user_message = None
        for i, msg in enumerate(reversed(messages)):
            logger.debug(f"Message {i}: role={msg.get('role')}, content_length={len(msg.get('content', ''))}")
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                logger.info(f"Found user message: {user_message[:100]}...")
                break

        if not user_message:
            logger.warning("No user message found in messages")
            return jsonify({'error': 'No user message found'}), 400

        logger.info("🤖 Processing query with RAG system...")
        rag = get_rag_system()

        logger.debug(f"Querying with k=5, message length: {len(user_message)}")
        answer = rag.query(
            question=user_message,
            k=5,
            repo_filter=None,
            verbose=False
        )

        logger.info(f"✅ Query processed, answer length: {len(answer)}")
        logger.debug(f"Answer preview: {answer[:200]}...")

        response = {
            "model": os.getenv('OLLAMA_MODEL', 'llama3.2:3b'),
            "created_at": datetime.now().isoformat(),
            "message": {
                "role": "assistant",
                "content": answer
            },
            "done": True
        }

        response = jsonify(response)
        response.headers['Content-Type'] = 'application/json'
        logger.debug("Returning chat response")
        return response

    except Exception as e:
        logger.error(f"❌ Chat endpoint failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_response = jsonify({'error': str(e)})
        error_response.headers['Content-Type'] = 'application/json'
        return error_response, 500

@app.route('/api/generate', methods=['POST'])
def ollama_generate():
    """Ollama-compatible endpoint for generation"""
    logger.info("🔧 Generate endpoint requested")
    try:
        data = request.json
        logger.debug(f"Generate request data: {data}")

        prompt = data.get('prompt', '')
        logger.debug(f"Prompt length: {len(prompt)}")

        if not prompt:
            logger.warning("No prompt provided in generate request")
            return jsonify({'error': 'Prompt is required'}), 400

        logger.info("🤖 Processing generation with RAG system...")
        rag = get_rag_system()

        logger.debug(f"Querying with k=5, prompt length: {len(prompt)}")
        answer = rag.query(
            question=prompt,
            k=5,
            repo_filter=None,
            verbose=False
        )

        logger.info(f"✅ Generation processed, answer length: {len(answer)}")
        logger.debug(f"Answer preview: {answer[:200]}...")

        response = {
            "model": os.getenv('OLLAMA_MODEL', 'llama3.2:3b'),
            "created_at": datetime.now().isoformat(),
            "response": answer,
            "done": True
        }

        response = jsonify(response)
        response.headers['Content-Type'] = 'application/json'
        logger.debug("Returning generate response")
        return response

    except Exception as e:
        logger.error(f"❌ Generate endpoint failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_response = jsonify({'error': str(e)})
        error_response.headers['Content-Type'] = 'application/json'
        return error_response, 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    logger.info("📊 Stats endpoint requested")
    try:
        rag = get_rag_system()
        stats = rag.db.get_stats()
        logger.info(f"Database stats retrieved: {stats}")
        response = jsonify({
            'database_stats': stats,
            'model': os.getenv('OLLAMA_MODEL', 'llama3.2:3b'),
            'total_points': stats.get('total_points', 0)
        })
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        logger.error(f"❌ Stats endpoint failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_response = jsonify({'error': str(e)})
        error_response.headers['Content-Type'] = 'application/json'
        return error_response, 500

# Add request logging middleware
@app.before_request
def log_request_info():
    logger.debug(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {dict(request.headers)}")
    # Only try to log JSON data for POST/PUT requests
    if request.method in ['POST', 'PUT'] and request.is_json:
        logger.debug(f"JSON data: {request.json}")

@app.after_request
def log_response_info(response):
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response size: {len(response.get_data())} bytes")
    return response

if __name__ == '__main__':
    logger.info("🚀 Starting Cline Integration Server...")
    logger.info("📍 Available endpoints:")
    logger.info("   GET  /health - Check system status")
    logger.info("   GET  /api/tags - Ollama model listing")
    logger.info("   POST /api/chat - Chat endpoint (Cline)")
    logger.info("   POST /api/generate - Generate endpoint")
    logger.info("   GET  /stats  - Database statistics")
    logger.info("🔗 Configure Cline: http://localhost:5001")
    logger.info("🎯 Using your embeddings + Ollama for context-aware responses!")
    logger.info("📝 Logs will be saved to: cline_integration.log")

    try:
        logger.info("🌐 Starting Flask server on 0.0.0.0:5001...")
        app.run(host='0.0.0.0', port=5001, debug=False)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
