from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
from dotenv import load_dotenv
from llm_service import LLMService
from nl_converter import NLConverter
import logging

# Set up Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
db_path = os.getenv("DB_PATH")

# Check for environment variable issues at startup
if not api_key or not db_path:
    logger.error("API key or DB path not found in environment variables.")

# Initialize services
try:
    llm_service = LLMService(api_key=api_key, db_path=db_path)
    nl_converter = NLConverter(api_key=api_key)
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    raise e


@app.route("/")
def index():
    return render_template("index.html")  # HTML for the input form


@app.route("/query", methods=["POST"])
def process_query():
    try:
        natural_query = request.form.get("natural_query", "").strip()

        if not natural_query:
            return jsonify({"success": False, "error": "Please enter a valid query."}), 400

        # Convert to SQL
        sql_result = llm_service.convert_to_sql_query(natural_query)

        if not sql_result["success"]:
            return jsonify({"success": False, "error": f"Error generating SQL query: {sql_result['error']}"}), 500

        # Execute query
        query_result = llm_service.execute_query(sql_result["query"])

        if not query_result["success"]:
            return jsonify({"success": False, "error": f"Error executing query: {query_result['error']}"}), 500

        # Convert to Natural Language Explanation using NER entities
        nl_result = nl_converter.convert_to_natural_language(query_result, natural_query)

        if not nl_result["success"]:
            return jsonify({"success": False, "error": f"Error generating explanation: {nl_result['error']}"}), 500

        # Prepare response
        response = {
            "success": True,
            "sql_query": sql_result["query"],
            "query_results": query_result["results"],
            "columns": query_result["columns"],
            "nl_explanation": nl_result["explanation"],
        }
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
