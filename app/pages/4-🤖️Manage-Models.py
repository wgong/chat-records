"""
Note:

- st.data_editor() does not yet support row-selection, will use aggrid for now
    - https://discuss.streamlit.io/t/experimental-data-editor-how-to-retrieve-selection/40518
"""

from helper import *

st.subheader("🤖️ Manage Models")


def main():
    TABLE_NAME = CFG["TABLE_MODEL"]
    search_term = st.text_input("🔍Keyword Search:", key="search_model").strip()
    if search_term:
        where_clause = f"""
            (name||description||tags) like '%{search_term}%'
        """
    else:
        where_clause = " 1=1 "

    df = None
    with DBConn() as _conn:
        sql_stmt = f"""
            select 
                name, url, description, tags, ts, uid, id
            from {TABLE_NAME}
            where {where_clause}
            order by ts desc, name
        """
        df = pd.read_sql(sql_stmt, _conn)

    # if df is None or not df.shape[0]:
    #     return

    grid_resp = ui_display_df_grid(df, selection_mode="single", clickable_columns=["url"])
    selected_rows = grid_resp['selected_rows']

    # display form
    selected_row = selected_rows[0] if len(selected_rows) else None
    ui_layout_form(selected_row, TABLE_NAME)

main()