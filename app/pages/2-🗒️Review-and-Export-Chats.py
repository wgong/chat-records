"""
Note:

- st.data_editor() does not yet support row-selection, will use aggrid for now
    - https://discuss.streamlit.io/t/experimental-data-editor-how-to-retrieve-selection/40518
"""

from utils import *

st.subheader("🗒️ Review & Export Chats")

def main():
    search_term = st.text_input("🔍Keyword Search:", key="search_view").strip()
    if search_term:
        where_clause = f"""
            (session_title||question||answer||topic||tags) like '%{search_term}%'
        """
    else:
        where_clause = " 1=1 "

    df = None
    with DBConn() as _conn:
        sql_stmt = f"""
            select 
                session_title, seq_num, question, answer, topic, tags, bot_name, ts, uid, id
            from {CFG["TABLE_CHATS"]}
            where {where_clause}
            order by ts desc, session_title, seq_num
        """
        df = pd.read_sql(sql_stmt, _conn)

    grid_response = ui_display_df_grid(df, selection_mode="multiple")

    if df is None or not df.shape[0]:
        return

    ts = get_ts_now()
    st.download_button(
        label="📥Export DB to CSV",
        data=convert_df2csv(df, index=False),
        file_name=f"exported-chat-records-{ts}.csv",
        mime='text/csv',
        key="export_db2csv"
    )

    for row in grid_response['selected_rows']:
        seq_num, question, answer, bot_name = row["seq_num"], row["question"], row["answer"], row["bot_name"]
        st.markdown(f"""##### <span style="color:red">Q [{seq_num}] :</span>""", unsafe_allow_html=True)
        st.markdown(question, unsafe_allow_html=True)
        st.markdown(f"""##### <span style="color:blue">{bot_name} [{seq_num}] :</span>""", unsafe_allow_html=True)
        st.markdown(answer, unsafe_allow_html=True)



main()