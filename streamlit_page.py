import os

from main_console import get_llm_response
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import streamlit as st

# Define variables
llm = ChatOpenAI(model='gpt-4-0613')
thought_llm = ChatOpenAI(model='gpt-4-0613')
# messages = []

# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
#     "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    
st.title("💬 School Assistant") 

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    # if not openai_api_key:
    #     st.info("Please add your OpenAI API key to continue.")
    #     st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = get_llm_response(messages=st.session_state.messages, llm=llm, thought_llm=thought_llm)
    msg = response.choices[0].message
    st.session_state.messages.append(msg)
    st.chat_message("assistant").write(msg.content)