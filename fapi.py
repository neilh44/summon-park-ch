import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any
from token_manager import TokenManager  

# Import your existing modules (assuming they are in the same directory)
from llm_service import LLMService
from ai_assistant import AIAssistant
from token_manager import TokenManager  # You'll need to extract TokenManager to a separate file

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Global service initializations
llm_service = None
ai_assistant = None
token_manager = None

def initialize_services():
    """Initialize services on app startup."""
    global llm_service, ai_assistant, token_manager
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    db_path = os.getenv("DB_PATH")

    if not api_key or not db_path:
        logger.error("Missing API key or database path in environment variables.")
        return False

    try:
        llm_service = LLMService(api_key=api_key, db_path=db_path)
        ai_assistant = AIAssistant(api_key=api_key)
        token_manager = TokenManager()
        return True
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        return False

def generate_default_followup_questions(user_input: str, df: pd.DataFrame) -> List[str]:
    """
    Generate default follow-up questions based on the user input and query results.
    """
    if df is None or df.empty:
        return [
            "Can you rephrase your query?",
            "Would you like to try a different search?",
            "Do you want to broaden the search criteria?"
        ]
    
    default_questions = [
        "Can you provide more details about these results?",
        "What insights can we draw from these results?",
        "Are there any specific trends you'd like to explore?"
    ]
    
    return default_questions

def process_user_input(user_input: str):
    """
    Process the user's input, generate a SQL query, execute it, and return results with AI assistant explanation.
    """
    try:
        # Process with AI Assistant first
        assistant_response = ai_assistant.process_query(user_input)
        if not assistant_response["success"]:
            error_info = ai_assistant.handle_error(assistant_response["error"])
            raise Exception(error_info["error_message"])

        # Convert to SQL
        sql_result = llm_service.convert_to_sql_query(user_input)
        if not sql_result["success"]:
            raise Exception(f"SQL Conversion Error: {sql_result['error']}")

        # Execute query
        query_result = llm_service.execute_query(sql_result["query"])
        if not query_result["success"]:
            raise Exception(f"Query Execution Error: {query_result['error']}")

        # Format results as a DataFrame
        results_df = pd.DataFrame(query_result["results"], columns=query_result["columns"])

        # Generate explanation using AI Assistant
        explanation = assistant_response.get("explanation", "Results processed successfully.")
        
        # Generate follow-up questions
        followup_questions = generate_default_followup_questions(user_input, results_df)
        
        return {
            "success": True,
            "results": results_df.to_dict(orient='records'),
            "columns": results_df.columns.tolist(),
            "explanation": explanation,
            "followup_questions": followup_questions
        }

    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/api/query', methods=['POST'])
def handle_query():
    """Handle user query endpoint."""
    data = request.json
    user_input = data.get('query', '').strip()

    if not user_input:
        return jsonify({
            "success": False, 
            "error": "Query cannot be empty"
        }), 400

    result = process_user_input(user_input)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy", 
        "services": {
            "llm_service": llm_service is not None,
            "ai_assistant": ai_assistant is not None
        }
    }), 200

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """Global error handler."""
    logger.error(f"Unexpected error: {str(e)}")
    return jsonify({
        "success": False, 
        "error": "An unexpected error occurred",
        "details": str(e)
    }), 500

def main():
    # Initialize services before running the app
    if not initialize_services():
        logger.error("Failed to initialize services. Cannot start the app.")
        return
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()