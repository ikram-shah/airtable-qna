"""
Sidebar
"""

import streamlit as st
from utils import (
    validate_api_key,
    validate_pat,
    validate_base_url,
    populate_markdown
)

def set_openai_api_key(api_key: str):
    """
    Sets the OpenAI API key in the session state.
    """
    st.session_state["OPENAI_API_KEY"] = api_key

def set_airtable_personal_access_token(airtable_pat: str):
    """
    Sets the Airtable personal access token in the session state.
    """
    st.session_state["AIRTABLE_PAT"] = airtable_pat

def set_airtable_base_url(airtable_url: str):
    """
    Sets the Airtable base URL in the session state.
    """
    st.session_state["AIRTABLE_URL"] = airtable_url

def setup():
    """
    Displays a sidebar with input and info contents.
    """
    with st.sidebar:
        
        api_key_input, airtable_pat_input, airtable_base_url_input = populate_markdown()

        if st.button('Configure', use_container_width=True):
            if validate_api_key(api_key_input) and validate_pat(airtable_pat_input) and validate_base_url(airtable_base_url_input):
                st.session_state["is_key_configured"] = True
                st.success('Successfully Configured!', icon="✅")
            else:
                st.session_state["is_key_configured"] = False
                error_message = 'Configuration failed. Please check the following input(s):'
                if not validate_api_key(api_key_input):
                    error_message += '\n- OpenAI API Key format is invalid (should start with "sk-")'
                if not validate_pat(airtable_pat_input):
                    error_message += '\n- Airtable Personal Access Token format is invalid (should start with "pat")'
                if not validate_base_url(airtable_base_url_input):
                    error_message += '\n- Airtable Base URL format is invalid (should start with "https://airtable.com" and have the correct path)'
                st.error(error_message, icon="🚨")

        if api_key_input:
            set_openai_api_key(api_key_input)
        if airtable_pat_input:
            set_airtable_personal_access_token(airtable_pat_input)
        if airtable_base_url_input:
            set_airtable_base_url(airtable_base_url_input)

        st.markdown("---")
        st.markdown(
            "This tool is a work in progress. You can contribute to the project on [GitHub](https://github.com/ikram-shah/airtable-qna)"
        )
        st.markdown("Made by [ikramshah](https://twitter.com/ikram_shah_v)")