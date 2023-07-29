import streamlit as st
import pandas as pd
from io import StringIO 
from helper import *

st.subheader("Import Chats")

def import_chat():

    df_chat = None
    INPUT_FILENAME = ""
    html_txt = ""
    cells = []
    CHAT_BOTS = CFG["CHAT_BOTS"]
    SUPPORTED_CHAT_BOTS = CFG["SUPPORTED_CHAT_BOTS"]

    c0, c1 = st.columns([6,3])
    with c1:
        st.markdown("""##### <span style="color:green">Upload a saved chat HTML file</span>""", unsafe_allow_html=True)
        bot_name = st.selectbox("Select AI Assistant Name", CHAT_BOTS, index=CHAT_BOTS.index("Claude - v2"))

        if bot_name not in SUPPORTED_CHAT_BOTS:
            st.error(f"{bot_name} is unsupported yet")
            return

        txt_file = st.file_uploader("", key="upload_txt")

        if txt_file is not None:
            INPUT_FILENAME = txt_file.name
            # To convert to a string based IO:
            html_txt = StringIO(txt_file.getvalue().decode("utf-8")).read()

        if bot_name == CFG["SUPPORTED_CHAT_BOTS"][0] and html_txt:
            cells = parse_html_txt_claude(html_txt)
                
    if not cells or not INPUT_FILENAME:
        return

    with c0:
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
        chat_data.append([id, session_title, bot_name, ts, seq_num, question, answer, topic, tags, uid])
        seq_num += 1


    if not chat_data: return

    df_chat = pd.DataFrame(chat_data, columns=CFG["CHAT_COLUMNS"])
    if df_chat is None or not df_chat.shape[0]:
        return

    if CFG["DEBUG_FLAG"]:
        st.dataframe(df_chat)

    c1, c2, _, _ = st.columns([2,2,2,2])
    with c1:
        btn_save = st.button("Save to DB")

    with c2:
        # st.markdown("""#### <span style="color:green">Download chat to a CSV file</span>""", unsafe_allow_html=True)
        if chat_data and INPUT_FILENAME:
            out_filename = ".".join(INPUT_FILENAME.split(".")[:-1]) + ".csv"
            st.download_button(
                label="Download to CSV",
                data=convert_df2csv(df_chat, index=False),
                file_name=out_filename,
                mime='text/csv',
            )

    if btn_save:
        # save chats to DB
        with DBConn() as _conn:
            df_chat.to_sql(CFG["CHAT_TABLE"], _conn, if_exists='append', index=False)


import_chat()