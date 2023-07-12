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
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType

from pyairtable import Table

airtable_logo_url = "https://seeklogo.com/images/A/airtable-logo-216B9AF035-seeklogo.com.png"
models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-0613", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613"]

def extract_ids_from_base_url(base_url):
    """
    Extract base and table ID or name from the base URL using regular expressions
    """
    pattern = r'https://airtable.com/([\w\d]+)/(.*?)(?:/|$)'
    match = re.match(pattern, base_url)
  
    if match:
        base_id = match.group(1)
        table_id = match.group(2)

        return dict(base_id=base_id, table_id=table_id)
    else:
        raise ValueError("Invalid base URL")

def airtable_to_csv():
    """
    Convert Airtable contents into csv
    """
    access_token = st.session_state["AIRTABLE_PAT"]
    
    # Extract the base and table ID from the base URL
    ids_from_url = extract_ids_from_base_url(st.session_state["AIRTABLE_URL"]) 
    base_id, table_id = ids_from_url['base_id'], ids_from_url['table_id']
    
    # Initialize Airtable Python SDK
    table = Table(access_token, base_id, table_id)

    # Get all records from the table
    all_records = table.all()

    # Extract the data from the JSON response and create a pandas DataFrame
    rows = []
    for record in all_records:
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
    openai_model_chosen = st.session_state["OPENAI_MODEL_CHOSEN"]
    agent = create_csv_agent(ChatOpenAI(openai_api_key=openai_key, model=openai_model_chosen, temperature=0), file_name, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS, agent_executor_kwargs={"handle_parsing_errors":True})
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
    st.set_page_config(page_title="Airtable-QnA", page_icon=im, layout="wide")
    st.image(airtable_logo_url, width=50)
    st.header("Airtable-QnA")
    
def populate_markdown():
    """
    Populates markdown for sidebar.
    """
    st.markdown("## Configuration")
    st.write("\n")
    st.session_state["OPENAI_MODEL_CHOSEN"] = st.selectbox('OpenAI Model', models, key='model', help="Learn more at [OpenAI Documentation](https://platform.openai.com/docs/models/)")
    api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="You can get your API key from [OpenAI Platform](https://platform.openai.com/account/api-keys)", 
            value=st.session_state.get("OPENAI_API_KEY", ""))
    airtable_pat_input = st.text_input(
            "Airtable Personal Access Token",
            type="password",
            placeholder="pat...",
            help="You can get your Airtable PAT from [Airtable](https://airtable.com/developers/web/guides/personal-access-tokens#creating-a-token)",
            value=st.session_state.get("AIRTABLE_PAT", ""))
    airtable_base_url_input = st.text_input(
            "Airtable Base URL",
            type="default",
            placeholder="https://airtable.com/app.../tbl...",
            help="You can get your Airtable Base URL by simply copy pasting the URL",
            value=st.session_state.get("AIRTABLE_URL", ""))
    return api_key_input, airtable_pat_input, airtable_base_url_input