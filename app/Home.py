"""

"""

import streamlit as st
import pandas as pd
from helper import *

st.set_page_config(
     page_title='Chat-Records',
     layout="wide",
     initial_sidebar_state="expanded",
)


st.markdown("""
## Chat Records
An app to import/export, manage chat records from dialog with AI assistants like [Claude](https://claude.ai/chats), [Bard](https://bard.google.com/).
            
It is built on [Streamlit](https://streamlit.io/) web framework ([Source @ GitHub](https://github.com/wgong/chat-records)) : 
- import chat-records from a saved HTML file or an exported CSV file;
- use beautifulsoup to parse the HTML file;
- store question-and-answers in an SQLite database; 
- search and manage chat records;


""", unsafe_allow_html=True)

# load config params into memory
# st.session_state["CHAT_TABLE"] = CFG["CHAT_TABLE"]

# detect table's existence, if no, create it
with DBConn() as _conn:
    try:
        sql_stmt = f"""
            select count(*) from {CFG["CHAT_TABLE"]};
        """
        pd.read_sql(sql_stmt, _conn)
    except Exception as ex:
        create_table_sql = f"""
            create table if not exists {CFG["CHAT_TABLE"]} 
            (
                id text NOT NULL,
                session_title text NOT NULL,
                bot_name text NOT NULL,
                ts text,
                seq_num text,
                question text,
                answer text,
                topic text,
                tags text,
                uid text
            );
        """
        db_run_sql(create_table_sql, _conn)

