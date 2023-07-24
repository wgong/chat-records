"""
Note:

- st.data_editor() does not yet support row-selection, will use aggrid for now
    - https://discuss.streamlit.io/t/experimental-data-editor-how-to-retrieve-selection/40518
"""

import streamlit as st
import pandas as pd

from helper import *

st.subheader("Manage Chats")

def main():
    df = None
    with DBConn() as _conn:
        sql_stmt = f"""
            select 
                session_title, seq_num, question, answer, ts, bot_name, bot_version
            from {st.session_state["CHAT_TABLE"]}
            order by ts desc, session_title, seq_num
        """
        df = pd.read_sql(sql_stmt, _conn)

    if df is None:
        return
    
    grid_response = display_df_grid(df, selection_mode="multiple")

    for row in grid_response['selected_rows']:
        seq_num, question, answer, bot_name = row["seq_num"], row["question"], row["answer"], row["bot_name"]
        st.markdown(f"""##### <span style="color:red">Q [{seq_num}] :</span>""", unsafe_allow_html=True)
        st.markdown(question, unsafe_allow_html=True)
        st.markdown(f"""##### <span style="color:blue">{bot_name} [{seq_num}] :</span>""", unsafe_allow_html=True)
        st.markdown(answer, unsafe_allow_html=True)


main()