import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from google.api_core.exceptions import ResourceExhausted

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with WD Bing!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",  # Page layout option
)

# Get API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display the chatbot's title on the page
st.title("🦾 WD Bing Gallage")
st.title("This is WD Chatbot. Made by Dinith Wishwajith Gallage.")
st.title("You can Click below text Field and you can Type what you want to know anything!")

# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Input field for user's message
user_prompt = st.chat_input("Ask Something...")

if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)
    
    # Try to get response with error handling
    try:
        # Send user's message to Gemini-Pro and get the response
        gemini_response = st.session_state.chat_session.send_message(user_prompt)
        
        # Display Gemini-Pro's response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)
            
    except ResourceExhausted:
        # Handle API quota/resource limit error
        with st.chat_message("assistant"):
            st.error("I'm sorry, but I've reached my usage limit for now. Please try again later or with a shorter message.")
            
    except Exception as e:
        # Handle other potential errors
        with st.chat_message("assistant"):
            st.error(f"I encountered an error. Please try again with a different question.")
            # Optional: log the error (commented out for production)
            # st.error(f"Error details: {str(e)}")
