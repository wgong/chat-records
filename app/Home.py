"""
An example multi-page streamlit app 
from https://towardsdatascience.com/3-ways-to-create-a-multi-page-streamlit-app-1825b5b07c0f
"""

import streamlit as st
st.set_page_config(layout="wide")
st.markdown('# Main page')
st.markdown("""
    This is a demo of the native multipage implementation in Streamlit.
    Click on one of the 'pages' in the side bar to load a new page
""")