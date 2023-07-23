import sqlite3
import pandas as pd

from config import CFG

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