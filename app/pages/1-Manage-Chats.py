import streamlit as st
import pandas as pd
from io import StringIO 
from bs4 import BeautifulSoup
from lxml import html
from datetime import datetime

from helper import *


st.subheader("Manage Chats")

df = None
with DBConn() as _conn:
    sql_stmt = f"""
        select 
            session_title, seq_num, question, answer, ts, bot_name, bot_version
        from {st.session_state["CHAT_TABLE"]}
        order by ts desc, session_title, seq_num
    """
    df = pd.read_sql(sql_stmt, _conn)

if df is not None:
    st.dataframe(df)