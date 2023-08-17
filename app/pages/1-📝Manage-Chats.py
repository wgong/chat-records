"""
Note:

- st.data_editor() does not yet support row-selection, will use aggrid for now
    - https://discuss.streamlit.io/t/experimental-data-editor-how-to-retrieve-selection/40518
"""

from utils import *

st.subheader("📝 Manage Chats")

def main():
    TABLE_NAME = CFG["TABLE_CHATS"]
    search_term = st.text_input("🔍Keyword Search:", key="search_update").strip()
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
                session_title, seq_num, question, answer, topic, tags, ts, bot_name, uid, id
            from {TABLE_NAME}
            where {where_clause}
            order by ts desc, session_title, seq_num
        """
        df = pd.read_sql(sql_stmt, _conn)

    grid_resp = ui_display_df_grid(df, selection_mode="single")
    selected_rows = grid_resp['selected_rows']

    # display form
    selected_row = selected_rows[0] if len(selected_rows) else None
    ui_layout_form(selected_row, TABLE_NAME)

main()