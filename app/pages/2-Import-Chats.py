import streamlit as st
import pandas as pd
# import plotly.express as px
from io import StringIO 
from bs4 import BeautifulSoup
from lxml import html
from datetime import datetime

from helper import *




CHAT_BOTS = ["Claude __ v2", "Bard __ beta"]
SUPPORTED_CHAT_BOTS = ["Claude __ v2"]
NOISE_WORDS = ['Copy code','Copy']

df_chat = None

st.subheader("Import Chats")

def convert_df2csv(df, index=True):
    return df.to_csv(index=index).encode('utf-8')

def convert_htm2txt(html_txt):
    return html.fromstring(html_txt).text_content().strip()

def is_noise_word(html_txt):
    return convert_htm2txt(html_txt) in NOISE_WORDS

def _parse_bot_ver(bot_ver, sep="__"):
    return [x.strip() for x in bot_ver.split(sep) if x.strip()]

def parse_html_txt_claude(html_txt):
    """
    Extract question/answer from HTML text

    Returns:
        list of dialog content
    """
    cells = []
    if not html_txt: return cells

    soup = BeautifulSoup(html_txt, "html.parser")
    results = soup.findAll("div", class_="contents")
    for i in range(len(results)):
        v = results[i].prettify()
        if is_noise_word(v): continue
        # important to preserve HTML string because python code snippets are formatted
        cells.append(v)
    return cells

def import_chat():


    INPUT_FILENAME = ""
    html_txt = ""
    cells = []

    c0, c1 = st.columns([6,3])
    with c1:
        st.markdown("""##### <span style="color:green">Upload a saved chat HTML file</span>""", unsafe_allow_html=True)
        bot = st.selectbox("Select AI Assistant Name", CHAT_BOTS, index=CHAT_BOTS.index("Claude __ v2"))

        if bot not in SUPPORTED_CHAT_BOTS:
            st.error(f"{bot} is unsupported yet")
            return

        bot_name, bot_version = _parse_bot_ver(bot)

        txt_file = st.file_uploader("", key="upload_txt")

        if txt_file is not None:
            INPUT_FILENAME = txt_file.name
            # To convert to a string based IO:
            html_txt = StringIO(txt_file.getvalue().decode("utf-8")).read()

        if bot_name == "Claude" and html_txt:
            cells = parse_html_txt_claude(html_txt)
                
    if not cells or not INPUT_FILENAME:
        return

    with c0:
        session_title = " ".join(INPUT_FILENAME.split(".")[:-1])
        st.markdown(f"""##### <span style="color:green">{session_title}</span>
- {int(len(cells)/2)} questions are asked in this session
            """, unsafe_allow_html=True)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_data = []
    seq_num = 1
    cell_length = len(cells)
    for i in range(0, len(cells), 2):
        question = cells[i] if i < cell_length else ""
        answer = cells[i+1] if (i+1) < cell_length else ""
        st.markdown(f"""##### <span style="color:red">Q [{seq_num}] :</span>""", unsafe_allow_html=True)
        st.markdown(question, unsafe_allow_html=True)
        st.markdown(f"""##### <span style="color:blue">A [{seq_num}] :</span>""", unsafe_allow_html=True)
        st.markdown(answer, unsafe_allow_html=True)
        chat_data.append([session_title, bot_name, bot_version, ts, seq_num, question, answer])
        seq_num += 1


    if not chat_data: return

    df_chat = pd.DataFrame(chat_data, columns=st.session_state["CHAT_COLUMNS"])
    if df_chat is None or not df_chat.shape[0]:
        return

    if st.session_state["DEBUG_FLAG"]:
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
            df_chat.to_sql(st.session_state["CHAT_TABLE"], _conn, if_exists='append', index=False)


import_chat()