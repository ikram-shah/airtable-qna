"""
Airtable-QnA
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

query = st.text_area("Ask anything to your Airtable records \n ",label_visibility="visible", placeholder="How many records have...?", on_change=clear_submit)

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

