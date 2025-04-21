import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import traceback

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with WD Bing!",
    page_icon=":brain:",
    layout="centered",
)

# Get API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Debug mode for development (set to False in production)
DEBUG_MODE = True

# Set up Google Gemini-Pro AI model
if GOOGLE_API_KEY:
    try:
        gen_ai.configure(api_key=GOOGLE_API_KEY)
        model = gen_ai.GenerativeModel('gemini-pro')
        st.session_state.api_configured = True
    except Exception as e:
        st.error(f"Failed to configure API: {str(e) if DEBUG_MODE else 'Check your API key'}")
        st.session_state.api_configured = False
else:
    st.error("API key not found. Please check your .env file.")
    st.session_state.api_configured = False

# Function to translate roles
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Initialize chat session if API is configured
if st.session_state.get("api_configured", False) and "chat_session" not in st.session_state:
    try:
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"Failed to start chat: {str(e) if DEBUG_MODE else 'Unable to initialize chat'}")

# Display the chatbot's title
st.title("🦾 WD Bing Gallage")
st.title("This is WD Chatbot. Made by Dinith Wishwajith Gallage.")
st.title("You can Click below text Field and you can Type what you want to know anything!")

# Only proceed if API is configured
if st.session_state.get("api_configured", False) and "chat_session" in st.session_state:
    # Display chat history
    try:
        for message in st.session_state.chat_session.history:
            with st.chat_message(translate_role_for_streamlit(message.role)):
                st.markdown(message.parts[0].text)
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"Error displaying history: {str(e)}")
        # Continue even if history display fails

    # Input field for user's message
    user_prompt = st.chat_input("Ask Something...")

    if user_prompt:
        # Display user message
        st.chat_message("user").markdown(user_prompt)
        
        # Try to get response
        try:
            # Send message to Gemini
            gemini_response = st.session_state.chat_session.send_message(user_prompt)
            
            # Display response
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
                
        except Exception as e:
            with st.chat_message("assistant"):
                if DEBUG_MODE:
                    st.error(f"Error: {str(e)}")
                    st.code(traceback.format_exc(), language="python")
                else:
                    st.error("I encountered an error. Please try again with a different question.")
else:
    st.write("Please fix the API configuration issues to continue.")
