"""
Utility functions
"""

import re
from io import BytesIO
from PIL import Image
import tempfile
import streamlit as st
import requests
import pandas as pd

from langchain.agents import create_csv_agent
from langchain.llms import OpenAI

airtable_logo_url = "https://seeklogo.com/images/A/airtable-logo-216B9AF035-seeklogo.com.png"

def transform_base_url(base_url):
    """
    Extract base ID and table name from the base URL using regular expressions
    """
    pattern = r'https://airtable.com/([\w\d]+)/(.*?)(?:/|$)'
    match = re.match(pattern, base_url)
  
    if match:
        base_id = match.group(1)
        table_name = match.group(2)
      
        # Transform the base URL into the Airtable API URL format
        api_url = f'https://api.airtable.com/v0/{base_id}/{table_name}'
        return api_url
    else:
        raise ValueError("Invalid base URL")

def airtable_to_csv():
    """
    Convert Airtable contents into csv
    """
    access_token = st.session_state["AIRTABLE_PAT"]
    base_url = st.session_state["AIRTABLE_URL"]

    # Set headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Make the API request to get the records
    response = requests.get(transform_base_url(base_url), headers=headers)
    data = response.json()["records"]

    # Extract the data from the JSON response and create a pandas DataFrame
    rows = []
    for record in data:
        row = record['fields']
        row['id'] = record['id']
        rows.append(row)
    df = pd.DataFrame(rows)

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        df.to_csv(tmp_file.name, index=False)

    return tmp_file.name

def clear_submit():
    """
    Clears the 'submit' value in the session state.
    """
    st.session_state["submit"] = False

def run_agent(file_name, query):
    """
    Runs the agent on the given file with the specified query.
    """
    openai_key = st.session_state["OPENAI_API_KEY"]
    agent = create_csv_agent(OpenAI(temperature=0, openai_api_key=openai_key), file_name, verbose=True)
    return agent.run(query).__str__()

def validate_api_key(api_key_input):
    """
    Validates the provided API key.
    """
    api_key_regex = r"^sk-"
    api_key_valid = re.match(api_key_regex, api_key_input) is not None
    return api_key_valid

def validate_pat(airtable_pat_input):
    """
    Validates the provided Airtable personal access token (PAT).
    """
    airtable_pat_regex = r"^pat"
    airtable_pat_valid = re.match(airtable_pat_regex, airtable_pat_input) is not None
    return airtable_pat_valid

def validate_base_url(airtable_base_url_input):
    """
    Validates the provided Airtable base URL.
    """
    airtable_base_url_regex = r"^https:\/\/airtable.com\/app[^\/]+\/tbl[^\/]"
    airtable_base_url_valid = re.match(airtable_base_url_regex, airtable_base_url_input) is not None
    return airtable_base_url_valid

def set_logo_and_page_config():
    """
    Sets the Airtable logo image and page config.
    """
    response = requests.get(airtable_logo_url)
    im = Image.open(BytesIO(response.content))
    st.set_page_config(page_title="Airtable-QA", page_icon=im, layout="wide")
    st.image(airtable_logo_url, width=50)
    st.header("Airtable-QA")
    
def populate_markdown():
    """
    Populates markdown for sidebar.
    """
    st.markdown(
            "## How to use\n"
            "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below 🔑\n" 
            "2. Enter your Airtable Personal Access Token & Base URL 🔑\n"
            "3. Ask any question that can be answered from Airtable Base💬\n")
    api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="You can get your API key from https://platform.openai.com/account/api-keys", 
            value=st.session_state.get("OPENAI_API_KEY", ""))
    airtable_pat_input = st.text_input(
            "Airtable Personal Access Token",
            type="password",
            placeholder="pat...",
            help="You can get your Airtable PAT from https://airtable.com/developers/web/guides/personal-access-tokens#creating-a-token",
            value=st.session_state.get("AIRTABLE_PAT", ""))
    airtable_base_url_input = st.text_input(
            "Airtable Base URL",
            type="default",
            placeholder="https://airtable.com/app.../tbl...",
            help="You can get your Airtable Base URL by simply copy pasting the URL",
            value=st.session_state.get("AIRTABLE_URL", ""))
    return api_key_input, airtable_pat_input, airtable_base_url_input