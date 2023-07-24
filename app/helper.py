import sqlite3
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from lxml import html
from datetime import datetime
from st_aggrid import (GridOptionsBuilder, JsCode,
                       AgGrid, GridUpdateMode, DataReturnMode)

CFG = {
    "CHAT_TABLE" : "t_chats",
    "CHAT_COLUMNS" : ["session_title", "bot_name", "bot_version", "ts", "seq_num", "question", "answer"],
    "DB_FILENAME" : Path(__file__).parent / "chats.sqlite",
    "DEBUG_FLAG" : True,
}


CHAT_BOTS = ["Claude __ v2", "Bard __ beta"]
SUPPORTED_CHAT_BOTS = ["Claude __ v2"]
NOISE_WORDS = ['Copy code','Copy']

# Aggrid options
# how to set column width
# https://stackoverflow.com/questions/72624323/how-to-set-a-max-column-length-for-streamlit-aggrid
AGGRID_OPTIONS = {
    "paginationPageSize": 10,
    "grid_height": 360,
    "return_mode_value": DataReturnMode.__members__["FILTERED"],
    "update_mode_value": GridUpdateMode.__members__["MODEL_CHANGED"],
    "fit_columns_on_grid_load": True,
    "min_column_width": 4,
    "selection_mode": "single",  #  "multiple",  # 
    "allow_unsafe_jscode": True,
    "groupSelectsChildren": True,
    "groupSelectsFiltered": True,
    "enable_pagination": True,
}

class DBConn(object):
    def __init__(self, db_file=CFG["DB_FILENAME"]):
        self.conn = sqlite3.connect(db_file)

    def __enter__(self):
        return self.conn

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

def run_sql(sql_stmt, conn=None):
    if not sql_stmt or conn is None:
        return None
    
    if sql_stmt.lower().strip().startswith("select"):
        return pd.read_sql(sql_stmt, conn)
    
    cur = conn.cursor()
    cur.executescript(sql_stmt)
    conn.commit()
    conn.close()
    return None

def display_df_grid(df, 
        selection_mode="single",  # "multiple", 
        fit_columns_on_grid_load=AGGRID_OPTIONS["fit_columns_on_grid_load"],
        min_column_width=AGGRID_OPTIONS["min_column_width"],
        page_size=AGGRID_OPTIONS["paginationPageSize"],
        grid_height=AGGRID_OPTIONS["grid_height"],
        clickable_columns=[],
        editable_columns=[],
        colored_columns={}
    ):
    """show input df in a grid and return selected row
    """

    gb = GridOptionsBuilder.from_dataframe(df, min_column_width=min_column_width)
    gb.configure_selection(selection_mode,
            use_checkbox=True,
            groupSelectsChildren=AGGRID_OPTIONS["groupSelectsChildren"], 
            groupSelectsFiltered=AGGRID_OPTIONS["groupSelectsFiltered"]
        )
    gb.configure_pagination(paginationAutoPageSize=False, 
        paginationPageSize=page_size)
    
    gb.configure_columns(editable_columns, editable=True)

    # color column
    for k,v in colored_columns.items():
        gb.configure_column(k, cellStyle=v)

    if clickable_columns:       # config clickable columns
        cell_renderer_url =  JsCode("""
            function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`}
        """)
        for col_name in clickable_columns:
            gb.configure_column(col_name, cellRenderer=cell_renderer_url)


    gb.configure_grid_options(domLayout='normal')
    grid_response = AgGrid(
        df, 
        gridOptions=gb.build(),
        data_return_mode=AGGRID_OPTIONS["return_mode_value"],
        update_mode=AGGRID_OPTIONS["update_mode_value"],
        height=grid_height, 
        # width='100%',
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
    )
 
    return grid_response

def convert_df2csv(df, index=True):
    return df.to_csv(index=index).encode('utf-8')

def convert_htm2txt(html_txt):
    return html.fromstring(html_txt).text_content().strip()

def is_noise_word(html_txt):
    return convert_htm2txt(html_txt) in NOISE_WORDS

def parse_bot_ver(bot_ver, sep="__"):
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