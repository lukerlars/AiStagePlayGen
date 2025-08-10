import streamlit as st

# Initialize session state to store messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Title
st.title("Text Input App")

# Text input box
user_input = st.text_input("Enter your text here:")

# Add button to submit text
if st.button("Add Text"):
    if user_input:
        # Add new message to the beginning of the list
        st.session_state.messages.insert(0, user_input)
        # Clear the input box
        st.rerun()

# Display all messages
for message in st.session_state.messages:
    st.write(message)
    
