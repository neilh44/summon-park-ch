import streamlit as st
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables (if necessary)
load_dotenv()

# Set the endpoint URL for Groq API or use your custom API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Your actual Groq API key
API_URL = "https://api.groq.com/openai/v1/chat/completions"  # Groq API endpoint

# Initialize session state to store chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to call the Groq API for chat response using LLaMA3-8B-8192 model
def get_groq_response(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "LLaMA3-8B-8192",  # Model choice: LLaMA 3-8b
        "messages": messages
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Function to handle the chat interface (handles user input and API call)
def handle_chat():
    user_message = st.chat_input("What is up?")  # User input field
    
    if user_message:
        # Add user message to the session chat history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": timestamp
        })
        
        # Prepare messages for the API (user's input and previous chat history)
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]
        
        # Get response from Groq API or your model
        groq_response = get_groq_response(messages)
        
        # Check if response is valid
        if "error" in groq_response:
            bot_message = f"Error: {groq_response['error']}"
        else:
            bot_message = groq_response.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I didn't get that.")

        # Add bot's response to the session chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": bot_message,
            "timestamp": timestamp
        })

# Function to render the chat history using st.chat_message
def render_chat_history():
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Main function to run the app
def main():
    st.title("Chatbot with LLaMA 3-8b via Groq API")

    render_chat_history()  # Render the chat history with the chat history
    handle_chat()          # Handle user input and API call

if __name__ == "__main__":
    main()
