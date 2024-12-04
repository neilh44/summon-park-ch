import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from llm_service import LLMService
from ui_components import ClaudeUI, ChatHistory, ResponseCard
from ai_assistant import AIAssistant
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import tiktoken

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenManager:
    def __init__(self, model_name="llama3-8b-8192"):
        self.encoding = tiktoken.encoding_for_model(model_name)
        self.max_input_tokens = 15000  # Adjust based on your model's limits
        self.max_output_tokens = 4000   # Adjust based on your model's limits
        self.max_context_tokens = 10000 # Maximum context window size

    def count_tokens(self, text):
        """Count the number of tokens in a text string."""
        return len(self.encoding.encode(text))

    def truncate_text(self, text, max_tokens):
        """Truncate text to fit within token limit."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return self.encoding.decode(tokens[:max_tokens])

    def format_dataframe(self, df, max_tokens):
        """Format DataFrame as string with token limit."""
        df_str = df.to_string(index=False)
        return self.truncate_text(df_str, max_tokens)

    def get_context_window(self, messages, max_tokens):
        """Get recent message history that fits within token limit."""
        total_tokens = 0
        context_messages = []
        
        for message in reversed(messages):
            message_tokens = self.count_tokens(str(message))
            if total_tokens + message_tokens > max_tokens:
                break
            context_messages.insert(0, message)
            total_tokens += message_tokens
            
        return context_messages

def generate_default_followup_questions(user_input: str, df: pd.DataFrame) -> List[str]:
    """
    Generate default follow-up questions based on the user input and query results.
    
    Args:
        user_input (str): The original user input query.
        df (pd.DataFrame): The DataFrame containing query results.
    
    Returns:
        List[str]: A list of suggested follow-up questions.
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

def process_user_input(user_input, chat_history, llm_service, ai_assistant, conversation_id):
    """
    Process the user's input, generate a SQL query, execute it, and return results with AI assistant explanation.
    """
    try:
        # Add user message to chat history
        chat_history.add_message('user', user_input, conversation_id)

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
        
        # Format the complete response
        response = f"{explanation}\n\nQuery Results:\n{results_df.to_string(index=False)}"
        
        # Add follow-up questions if available
        if followup_questions:
            response += "\n\nSuggested follow-up questions:\n"
            for q in followup_questions:
                response += f"- {q}\n"
                
        chat_history.add_message('assistant', response, conversation_id)

        return results_df, explanation

    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
        chat_history.add_message('assistant', f"Error: {str(e)}", conversation_id)
        return None, f"Error: {str(e)}"

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    db_path = os.getenv("DB_PATH")

    if not api_key or not db_path:
        st.error("Missing API key or database path in environment variables.")
        logger.error("API key or DB path not found.")
        return

    # Initialize services
    try:
        llm_service = LLMService(api_key=api_key, db_path=db_path)
        ai_assistant = AIAssistant(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing services: {str(e)}")
        logger.error(f"Initialization error: {str(e)}")
        return

    # Initialize UI
    ui = ClaudeUI()

    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = ChatHistory()

    # Render title and sidebar
    ui.render_title()
    ui.render_sidebar()

    # Ensure there's a selected conversation
    if 'selected_conversation_id' not in st.session_state or not st.session_state.selected_conversation_id:
        st.session_state.selected_conversation_id = st.session_state.chat_history.create_new_conversation()

    # Handle user input
    user_input, submit_button = ui.render_input_form()

    if submit_button and user_input.strip():
        with st.spinner("Processing your query..."):
            try:
                # Process user input
                df, explanation = process_user_input(
                    user_input.strip(),
                    st.session_state.chat_history,
                    llm_service,
                    ai_assistant,
                    st.session_state.selected_conversation_id
                )
                
                # Display results using ResponseCard
                if df is not None:
                    # Generate follow-up questions
                    followup_questions = generate_default_followup_questions(user_input, df)
                    
                    ResponseCard.display(
                        response=df,
                        title="Query Results",
                        response_type="success",
                        explanation=explanation,
                        followup_questions=followup_questions
                    )
                else:
                    ResponseCard.error_card(
                        error_message="Could not process the query.",
                        suggestions=[
                            "Check your input",
                            "Verify database connection",
                            "Try a different query"
                        ]
                    )
            
            except Exception as e:
                # Handle any unexpected errors
                ResponseCard.error_card(
                    error_message=f"An unexpected error occurred: {str(e)}",
                    suggestions=[
                        "Retry the query",
                        "Check your input",
                        "Contact support if the issue persists"
                    ]
                )
                logger.error(f"Unexpected error in query processing: {str(e)}")

    # Render chat messages
    ui.render_chat_messages(
        st.session_state.chat_history, 
        st.session_state.selected_conversation_id
    )

if __name__ == "__main__":
    main()