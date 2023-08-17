"""
On 2023-07-30, Claude.AI starts blocking Save-HTML page, I can no longer save chat-records.
"""

from utils import *

st.subheader("📥Import Chats")

file_type = option_menu(None, 
    ["HTML", "CSV", ], 
    icons=["filetype-csv","filetype-html"],  # from https://icons.getbootstrap.com/
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "25px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#ABB7EB"},
    }
)

def safe_to_sql(df, conn):
    curr_row_count = db_get_row_count(CFG["TABLE_CHATS"])
    st.info(f"curr_row_count = {curr_row_count}")
    if curr_row_count < CFG["MAX_NUM_ROWS"]:
        df.to_sql(CFG["TABLE_CHATS"], conn, if_exists='append', index=False)
    else:
        st.error(f"""Table {CFG["TABLE_CHATS"]} has over {CFG["MAX_NUM_ROWS"]} rows, saving is disabled !""")


def import_chat_from_html():

    df_chat = None
    INPUT_FILENAME = ""
    html_txt = ""
    cells = []
    bot_names = db_get_llm_models()
    try:
        idx_default = bot_names.index("Claude - v2")
    except:
        idx_default = 0

    SUPPORTED_CHAT_BOTS = CFG["SUPPORTED_CHAT_BOTS"]

    TABLE_CHATS_COLUMNS = [c.split()[0]  for c in CFG["TABLES"][CFG["TABLE_CHATS"]]]

    c0, c1 = st.columns([4,4])
    with c0:
        st.markdown("""##### <span style="color:green">Upload an HTML file</span>""", unsafe_allow_html=True)
        bot_name = st.selectbox("Select AI Assistant Name", bot_names, index=idx_default)

        if bot_name not in SUPPORTED_CHAT_BOTS:
            st.error(f"{bot_name} is unsupported yet")
            return

        txt_file = st.file_uploader("", key="upload_txt")

        if txt_file is not None:
            INPUT_FILENAME = txt_file.name
            # To convert to a string based IO:
            html_txt = StringIO(txt_file.getvalue().decode("utf-8")).read()

        if bot_name == SUPPORTED_CHAT_BOTS[0] and html_txt:
            cells = parse_html_txt_claude(html_txt)
                
    if not cells or not INPUT_FILENAME:
        return

    with c1:
        session_title = " ".join(INPUT_FILENAME.split(".")[:-1])
        st.markdown(f"""##### <span style="color:green">{session_title}</span>
- {int(len(cells)/2)} questions are asked in this session
            """, unsafe_allow_html=True)

    ts = get_ts_now()
    chat_data = []
    seq_num = 1
    topic = tags = ""
    uid = get_uid()
    cell_length = len(cells)
    for i in range(0, len(cells), 2):
        id = get_uuid()
        question = cells[i] if i < cell_length else ""
        answer = cells[i+1] if (i+1) < cell_length else ""
        st.markdown(f"""##### <span style="color:red">Q [{seq_num}] :</span>""", unsafe_allow_html=True)
        st.markdown(question, unsafe_allow_html=True)
        st.markdown(f"""##### <span style="color:blue">A [{seq_num}] :</span>""", unsafe_allow_html=True)
        st.markdown(answer, unsafe_allow_html=True)

        row_dic = {
            "id": id,
            "session_title":session_title,
            "bot_name":bot_name,
            "ts":ts,
            "seq_num":seq_num,
            "question":question,
            "answer":answer,
            "topic":topic,
            "tags":tags,
            "uid":uid
        }
        row_data = []
        for c in TABLE_CHATS_COLUMNS:
            row_data.append(row_dic.get(c,""))
        chat_data.append(row_data)
        seq_num += 1


    if not chat_data: return

    df_chat = pd.DataFrame(chat_data, columns=TABLE_CHATS_COLUMNS)
    if df_chat is None or not df_chat.shape[0]:
        return

    if CFG["DEBUG_FLAG"]:
        st.dataframe(df_chat)

    c1, c2, _, _ = st.columns([2,2,2,2])
    with c1:
        btn_save = st.button("💾 Save to DB")

    with c2:
        # st.markdown("""#### <span style="color:green">Download chat to a CSV file</span>""", unsafe_allow_html=True)
        if chat_data and INPUT_FILENAME:
            out_filename = ".".join(INPUT_FILENAME.split(".")[:-1]) + ".csv"
            st.download_button(
                label="📥Download to CSV",
                data=convert_df2csv(df_chat, index=False),
                file_name=out_filename,
                mime='text/csv',
            )
    if btn_save:
        # save chats to DB
        with DBConn() as _conn:
            safe_to_sql(df_chat, _conn)


def import_chat_from_csv():
    df_imp = None
    csv_data = None
    _, c1 = st.columns([6,3])
    with c1:
        csv_file = st.file_uploader("Import CSV to DB", key="import_csv2db")
        if csv_file is not None:
            # INPUT_FILENAME = txt_file.name
            # To convert to a string based IO:
            csv_data = StringIO(csv_file.getvalue().decode("utf-8"))
            df_imp = pd.read_csv(csv_data)

    curr_row_count = db_get_row_count(CFG["TABLE_CHATS"])
    st.info(f"curr_row_count = {curr_row_count}")

    if df_imp is not None:
        # st.dataframe(df_imp)
        with DBConn() as _conn:
            df_imp["id"] = df_imp.apply(lambda r:  get_uuid(), axis=1)
            safe_to_sql(df_imp, _conn)

def main():
    if file_type == "CSV":
        import_chat_from_csv()
    elif file_type == "HTML":
        import_chat_from_html()

main()