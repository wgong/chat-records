"""
# TODO
[2023-07-29]
- add support for Bard chat-records
- deploy to streamlit cloud
- write a blog to share this app

- use option_menu (horizontally) to display CSV and HTML import (replacing expander)

# DONE
[2023-07-29]
- Completed basic functionality for Claude-2 chat-records

"""

from utils import *

st.set_page_config(
     page_title='Chat-Records',
     layout="wide",
     initial_sidebar_state="expanded",
)


st.markdown("""
## 😊 Chat Records 💬 
An app to import/export, manage chat records from dialog with AI assistants like [Claude](https://claude.ai/chats), [Bard](https://bard.google.com/).
            
It is built on [Streamlit](https://streamlit.io/) web framework ([Source @ GitHub](https://github.com/wgong/chat-records)) : 
- import chat-records from a saved HTML file or an exported CSV file;
- use beautifulsoup to parse the HTML file;
- store question-and-answers in an SQLite database; 
- search and manage chat records;


""", unsafe_allow_html=True)

# load config params into memory
# st.session_state["TABLE_CHATS"] = CFG["TABLE_CHATS"]

# detect table's existence, if no, create it

with DBConn() as _conn:
    for table_name in CFG["TABLES"].keys():
        db_create_table(table_name, _conn)

