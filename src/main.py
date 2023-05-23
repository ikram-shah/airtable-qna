"""
Airtable-QA
"""

import streamlit as st
from sidebar import setup as set_sidebar

from utils import (
    airtable_to_csv,
    run_agent,
    clear_submit,
    set_logo_and_page_config
)

set_logo_and_page_config()
set_sidebar()

st.caption('⚠️ This is experimental implementation, works for tables under 100 records due to Airtable WebAPI limitations.')
query = st.text_area("NOTE - Inspired from [Langchain CSV Agent](https://python.langchain.com/en/latest/modules/agents/toolkits/examples/csv.html). \n"
        "This agent calls the Pandas DataFrame agent under the hood, which in turn calls the Python agent, \n" 
        "which executes LLM generated Python code - this can be bad if the LLM generated Python code is harmful. **Use cautiously**."            ,
        label_visibility="visible", placeholder="Ask anything...", on_change=clear_submit)
button = st.button("Search")

if button or st.session_state.get("submit"):
    if not st.session_state.get("is_key_configured"):
        st.error("Please configure your OpenAI and Airtable keys!", icon="🚨")
    elif not query:
        st.error("Please enter a question!", icon="🚨")
    else:
        st.session_state["submit"] = True
        with st.spinner(text="Searching..."):
            agent_response = run_agent(airtable_to_csv(), query)
            st.write("#### Answer")
            st.write(agent_response)
            st.write("---")

