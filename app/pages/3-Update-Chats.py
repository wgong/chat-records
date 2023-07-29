"""
Note:

- st.data_editor() does not yet support row-selection, will use aggrid for now
    - https://discuss.streamlit.io/t/experimental-data-editor-how-to-retrieve-selection/40518
"""

import streamlit as st
import pandas as pd
from helper import *

st.subheader("Update Chats")

def ui_layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns):
    DISABLED = col in system_columns
    if old_row:
        old_val = old_row.get(col, "")
        widget_type = widget_types.get(col, "text_input")
        if widget_type == "text_area":
            kwargs = {"height":125}
            val = st.text_area(col_labels.get(col), value=old_val, disabled=DISABLED, key=f"col_{form_name}_{col}", kwargs=kwargs)
        elif widget_type == "date_input":
            old_date_input = old_val.split("T")[0]
            if old_date_input:
                val_date = datetime.strptime(old_date_input, "%Y-%m-%d")
            else:
                val_date = datetime.now().date()
            val = st.date_input(col_labels.get(col), value=val_date, disabled=DISABLED, key=f"col_{form_name}_{col}")
            val = datetime.strftime(val, "%Y-%m-%d")
        elif widget_type == "time_input":
            old_time_input = old_val
            if old_time_input:
                val_time = datetime.strptime(old_time_input.split(".")[0], "%H:%M:%S").time()
            else:
                val_time = datetime.now().time()
            val = st.time_input(col_labels.get(col), value=val_time, disabled=DISABLED, key=f"col_{form_name}_{col}")
        elif widget_type == "selectbox":
            # check if options is avail, otherwise display as text_input
            if col in SELECTBOX_OPTIONS:
                try:
                    if col == "ref_val":
                        _options = SELECTBOX_OPTIONS[col]()
                    else:
                        _options = SELECTBOX_OPTIONS.get(col,[])

                    old_val = old_row.get(col, "")
                    _idx = _options.index(old_val)
                    val = st.selectbox(col_labels.get(col), _options, index=_idx, key=f"col_{form_name}_{col}")
                except ValueError:
                    val = old_row.get(col, "")
            else:
                val = st.text_input(col_labels.get(col), value=old_val, disabled=DISABLED, key=f"col_{form_name}_{col}")

        else:
            val = st.text_input(col_labels.get(col), value=old_val, disabled=DISABLED, key=f"col_{form_name}_{col}")

        if val != old_val:
            data.update({col : val})

    return data


def ui_layout_form(selected_row, table_name="t_chats"):

    form_name = table_name
    COLUMN_DEFS = parse_column_props()
    COL_DEFS = COLUMN_DEFS[table_name]
    visible_columns = COL_DEFS["is_visible"]
    system_columns = COL_DEFS["is_system_col"]
    form_columns = COL_DEFS["form_column"]
    col_labels = COL_DEFS["label_text"]
    widget_types = COL_DEFS["widget_type"]

    old_row = {}
    for col in visible_columns:
        old_row[col] = selected_row.get(col, "") if selected_row is not None else ""

    data = {"table_name": table_name}

    # copy id if present
    id_val = old_row.get("id", "")
    if id_val:
        data.update({"id" : id_val})

    # display form and populate data dict
    col1_columns = []
    col2_columns = []
    for c in visible_columns:
        if form_columns.get(c, "").startswith("COL_1-"):
            col1_columns.append(c)
        elif form_columns.get(c, "").startswith("COL_2-"):
            col2_columns.append(c)

    with st.form(form_name, clear_on_submit=True):
        col1,col2 = st.columns([6,3])
        with col1:
            for col in col1_columns:
                data = ui_layout_form_fields(data,form_name,old_row,col,
                            widget_types,col_labels,system_columns)
        with col2:
            for col in col2_columns:
                data = ui_layout_form_fields(data,form_name,old_row,col,
                            widget_types,col_labels,system_columns)

            # add checkbox for deleting this record
            col = "delelte_record"
            delete_flag = st.checkbox("Delelte Record?", value=False)
            data.update({col: delete_flag})

        save_btn = st.form_submit_button("Save")
        if save_btn:
            try:
                delete_flag = data.get("delelte_record", False)
                if delete_flag:
                    if data.get("id"):
                        db_delete_by_id(data)
                else:
                    if data.get("id"):
                        data.update({"ts": get_ts_now(),
                                    "uid": get_uid(), })
                        db_update_by_id(data)
                    else:
                        data.update({"id": get_uuid(), 
                                    "ts": get_ts_now(),
                                    "uid": get_uid(), })
                        db_upsert(data)

            except Exception as ex:
                st.error(f"{str(ex)}")


def main():
    search_term = st.text_input("Search keyword:", key="search_update").strip()
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
            from {CFG["CHAT_TABLE"]}
            where {where_clause}
            order by ts desc, session_title, seq_num
        """
        df = pd.read_sql(sql_stmt, _conn)

    if df is None or not df.shape[0]:
        return

    grid_resp = display_df_grid(df, selection_mode="single")
    selected_rows = grid_resp['selected_rows']

    # display form
    selected_row = selected_rows[0] if len(selected_rows) else None
    ui_layout_form(selected_row)

main()