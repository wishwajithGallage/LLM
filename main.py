import os
import time
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import traceback
from google.api_core.exceptions import ResourceExhausted

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

# Maximum number of retries for rate limit errors
MAX_RETRIES = 3
# Base delay for exponential backoff (in seconds)
BASE_DELAY = 2

# Set up Google Gemini AI model
if GOOGLE_API_KEY:
    try:
        gen_ai.configure(api_key=GOOGLE_API_KEY)
        # Updated model name - use gemini-1.5-flash or gemini-1.5-pro
        model = gen_ai.GenerativeModel('gemini-1.5-flash')
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

# Function to send message with retry logic
def send_message_with_retry(chat_session, prompt):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            return chat_session.send_message(prompt)
        except ResourceExhausted as e:
            retries += 1
            if retries < MAX_RETRIES:
                # Exponential backoff
                delay = BASE_DELAY ** retries
                if DEBUG_MODE:
                    st.info(f"Rate limit exceeded. Retrying in {delay} seconds... (Attempt {retries}/{MAX_RETRIES})")
                time.sleep(delay)
            else:
                raise e
        except Exception as e:
            # For other exceptions, don't retry
            raise e

# Function to list available models (for debugging)
def list_available_models():
    try:
        models = gen_ai.list_models()
        return [model.name for model in models if 'generateContent' in model.supported_generation_methods]
    except Exception as e:
        return []

# Initialize chat session if API is configured
if st.session_state.get("api_configured", False) and "chat_session" not in st.session_state:
    try:
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"Failed to start chat: {str(e) if DEBUG_MODE else 'Unable to initialize chat'}")
        
        # Show available models for debugging
        if DEBUG_MODE:
            st.write("Available models:")
            available_models = list_available_models()
            for model_name in available_models:
                st.write(f"- {model_name}")

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
        
        # Create a placeholder for the response
        response_placeholder = st.empty()
        
        with st.chat_message("assistant"):
            try:
                # Show a "thinking" message
                with response_placeholder:
                    st.write("Thinking...")
                
                # Send message to Gemini with retry logic
                gemini_response = send_message_with_retry(st.session_state.chat_session, user_prompt)
                
                # Replace the placeholder with the actual response
                response_placeholder.empty()
                st.markdown(gemini_response.text)
                
            except ResourceExhausted:
                st.error("Rate limit exceeded. Please try again in a minute or consider upgrading your API quota.")
                if DEBUG_MODE:
                    st.code(traceback.format_exc(), language="python")
                
            except Exception as e:
                if DEBUG_MODE:
                    st.error(f"Error: {str(e)}")
                    st.code(traceback.format_exc(), language="python")
                else:
                    st.error("I encountered an error. Please try again with a different question.")
else:
    st.write("Please fix the API configuration issues to continue.")
    
    # Show debug information if API is not configured
    if DEBUG_MODE and GOOGLE_API_KEY:
        st.write("Debug: Attempting to list available models...")
        try:
            gen_ai.configure(api_key=GOOGLE_API_KEY)
            available_models = list_available_models()
            if available_models:
                st.write("Available models:")
                for model_name in available_models:
                    st.write(f"- {model_name}")
            else:
                st.write("No models found or unable to list models.")
        except Exception as e:
            st.error(f"Error listing models: {str(e)}")
