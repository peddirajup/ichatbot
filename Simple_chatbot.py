import streamlit as st


def chatbot_response(user_input):
    responses = {
        "hello": "Hi! How can I help you today?",
        "bye": "Goodbye ! Have a nice day!",
    }
    return responses.get(user_input.lower(), "I'm sorry, I didn't understand that. Can you rephrase?")


st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.write(message)

user_input = st.text_input("You:", "")

if st.button('Send'):
    if user_input:
        st.session_state.messages.append(f"You : {user_input}")
        bot_reply = chatbot_response(user_input)
        st.session_state.messages.append(f"Bot: {bot_reply}")
    # st.experimental_rerun()
