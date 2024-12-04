import streamlit as st
from datetime import datetime
from typing import Union, List, Dict, Any
import pandas as pd


class LLMService:
    def __init__(self):
        # Initialize any required LLM configurations here
        pass
        
    def process_query(self, query, conversation_history=None):
        """
        Process a query using the LLM service
        
        Args:
            query (str): The user's input query
            conversation_history (list): List of previous messages for context
            
        Returns:
            str: The LLM's response
        """
        try:
            # Here you would typically:
            # 1. Format the conversation history and query
            # 2. Make an API call to your LLM service
            # 3. Process and return the response
            
            # For now, returning a mock response
            return f"I understand you're asking about: {query}. How can I help further?"
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."

class ChatHistory:
    def __init__(self):
        self.messages = []
        self.conversations = {}
        self.current_conversation_id = None

    def add_message(self, role, content, conversation_id=None):
        timestamp = datetime.now().strftime("%I:%M %p")
        message = {
            'role': role,
            'content': content,
            'timestamp': timestamp,
        }

        if conversation_id is None:
            conversation_id = self.current_conversation_id

        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        self.conversations[conversation_id].append(message)
        self.messages = self.conversations[conversation_id]

    def get_conversation_pair(self, conversation_id):
        return self.conversations.get(conversation_id, [])

    def create_new_conversation(self):
        conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_conversation_id = conversation_id
        self.conversations[conversation_id] = []
        return conversation_id

    def get_conversation_history(self, conversation_id):
        """
        Get the conversation history in a format suitable for the LLM
        """
        messages = self.conversations.get(conversation_id, [])
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]


class ClaudeUI:
    def __init__(self):
        self.initialize_session_state()
        self.setup_layout()
        self.llm_service = LLMService()

    @staticmethod
    def initialize_session_state():
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = ChatHistory()
        if 'selected_conversation_id' not in st.session_state:
            st.session_state.selected_conversation_id = None
        if 'user_input' not in st.session_state:
            st.session_state.user_input = ""

    def setup_layout(self):
        st.set_page_config(
            layout="wide",
            page_title="Mr Parker by Summon",
            initial_sidebar_state="expanded"
        )
    
    def render_title(self):
        st.markdown("<h1>Welcome to Summon Valet Parking </h1>", unsafe_allow_html=True)    
    
    def render_sidebar(self):
        with st.sidebar:
            st.markdown('<div class="sidebar-title">Chat History</div>', unsafe_allow_html=True)

            if st.button("New Chat"):
                new_conversation_id = st.session_state.chat_history.create_new_conversation()
                st.query_params["conversation"] = new_conversation_id
                st.session_state.selected_conversation_id = new_conversation_id

            for conv_id, messages in st.session_state.chat_history.conversations.items():
                if messages:
                    first_message = messages[0]['content']
                    preview = first_message[:40] + "..." if len(first_message) > 40 else first_message
                    link = f"?conversation={conv_id}"
                    st.markdown(f"- [{preview}]({link})")

    def render_chat_messages(self, chat_history, selected_conversation_id=None):
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        if not selected_conversation_id:
            st.markdown('<div>No conversation selected. Start a new chat!</div>', unsafe_allow_html=True)
            return

        messages_to_display = chat_history.get_conversation_pair(selected_conversation_id)
        for msg in messages_to_display:
            self.render_message(msg)

        st.markdown('</div>', unsafe_allow_html=True)

    def render_message(self, msg):
        role_class = "user-message" if msg['role'] == 'user' else 'assistant-message'
        sender_name = 'You' if msg['role'] == 'user' else 'Mr Parker'

        st.markdown(f"""
            <div class="chat-message {role_class}">
                <div class="timestamp">{msg['timestamp']}</div>
                <div class="sender-name">{sender_name}</div>
                <div class="message-content">{msg['content']}</div>
            </div>
        """, unsafe_allow_html=True)

    def render_input_form(self):
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_area("Type your message...", key='user_input', height=100)
            col1, col2 = st.columns([5, 1])
            with col2:
                submit_button = st.form_submit_button("Send")
        st.markdown('</div>', unsafe_allow_html=True)
        return user_input, submit_button

    def process_user_input(self, user_input, conversation_id):
        """
        Process user input and get LLM response
        """
        # Get conversation history
        conversation_history = st.session_state.chat_history.get_conversation_history(conversation_id)
        
        # Process query through LLM service
        response = self.llm_service.process_query(user_input, conversation_history)
        
        return response

    def run(self):
        selected_conversation = st.query_params.get("conversation")
        if selected_conversation:
            st.session_state.selected_conversation_id = selected_conversation
        elif not st.session_state.selected_conversation_id:
            st.session_state.selected_conversation_id = st.session_state.chat_history.create_new_conversation()

        self.render_sidebar()

        user_input, submit_button = self.render_input_form()

        if submit_button and user_input:
            # Add user message
            st.session_state.chat_history.add_message(
                'user',
                user_input,
                st.session_state.selected_conversation_id
            )

            # Process user input and get response
            assistant_response = self.process_user_input(
                user_input,
                st.session_state.selected_conversation_id
            )

            # Add assistant response
            st.session_state.chat_history.add_message(
                'assistant',
                assistant_response,
                st.session_state.selected_conversation_id
            )

        self.render_chat_messages(
            st.session_state.chat_history,
            st.session_state.selected_conversation_id
        )

class ResponseCard:
    @staticmethod
    def display(
        response: Union[str, pd.DataFrame, Dict[str, Any]], 
        title: str = "Query Results", 
        response_type: str = "default",
        explanation: str = "",
        followup_questions: List[str] = None
    ):
        """
        Display a comprehensive response card in Streamlit
        
        Args:
            response: The main response content (text or DataFrame)
            title: Card title
            response_type: Type of response (success, error, insight, etc.)
            explanation: Detailed explanation of the response
            followup_questions: List of suggested follow-up questions
        """
        # Define color and icon mapping
        type_styles = {
            "success": {
                "color": "green",
                "icon": "✅",
                "message": "Successfully processed query"
            },
            "error": {
                "color": "red",
                "icon": "❌",
                "message": "Error in query processing"
            },
            "insight": {
                "color": "blue",
                "icon": "💡",
                "message": "Insights Generated"
            },
            "warning": {
                "color": "orange",
                "icon": "⚠️",
                "message": "Partial Results"
            },
            "default": {
                "color": "gray",
                "icon": "📊",
                "message": "Query Results"
            }
        }
        
        # Get style based on response type
        style = type_styles.get(response_type, type_styles["default"])
        
        # Create Streamlit container
        with st.container():
            # Card header with icon and title
            st.markdown(f"""
            <div style="
                background-color: {style['color']}20; 
                border-left: 4px solid {style['color']}; 
                padding: 10px; 
                margin-bottom: 10px;
                border-radius: 5px;
            ">
                <h3>{style['icon']} {title}</h3>
                <p style="color: {style['color']}; font-size: 0.9em;">
                    {style['message']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display explanation if provided
            if explanation:
                st.markdown(f"**Explanation:** {explanation}")
            
            # Display response content
            if isinstance(response, pd.DataFrame):
                # Display DataFrame
                st.dataframe(response)
            elif isinstance(response, dict):
                # Display dictionary as formatted JSON
                st.json(response)
            else:
                # Display as text
                st.markdown(str(response))
            
            # Follow-up Questions
            if followup_questions:
                st.markdown("### Suggested Follow-up Questions")
                cols = st.columns(len(followup_questions))
                for col, question in zip(cols, followup_questions):
                    with col:
                        if st.button(question, key=f"followup_{hash(question)}"):
                            # Trigger follow-up action if needed
                            st.session_state.user_input = question
        
        # Optional: Add a divider
        st.markdown("---")

    @staticmethod
    def error_card(
        error_message: str, 
        suggestions: List[str] = None
    ):
        """
        Display a dedicated error response card
        
        Args:
            error_message: Detailed error description
            suggestions: List of error recovery suggestions
        """
        st.error(error_message)
        
        if suggestions:
            st.markdown("### Suggested Fixes:")
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")

# Example usage in main application
def example_usage():
    # Simulating a successful query response
    response_data = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'San Francisco', 'Chicago']
    })
    
    followup_questions = [
        "Show age distribution",
        "Compare cities",
        "Filter by age"
    ]
    
    ResponseCard.display(
        response=response_data,
        title="User Demographics",
        response_type="success",
        explanation="Fetched user data successfully",
        followup_questions=followup_questions
    )

# Optional error handling demonstration
def example_error_handling():
    ResponseCard.error_card(
        error_message="Failed to retrieve data",
        suggestions=[
            "Check your database connection",
            "Verify query parameters",
            "Retry the query"
        ]
    )


if __name__ == "__main__":
    app = ClaudeUI()
    app.run()