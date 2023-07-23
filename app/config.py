from pathlib import Path

CFG = {
    "CHAT_TABLE" : "t_chats",
    "CHAT_COLUMNS" : ["session_title", "bot_name", "bot_version", "ts", "seq_num", "question", "answer"],
    "DB_FILENAME" : Path(__file__).parent / "chats.sqlite",
    "DEBUG_FLAG" : True,
}