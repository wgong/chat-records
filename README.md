# Chat-Records
Import and manage chat records with AI assistant like Claude, Bard


# Setup & Run

Create a virtual env with the latest streamlit release

```
########### create venv
$ python -m venv venv_st_latest
$ venv_st_latest\Scripts\activate.bat     # activate venv on Windows
$ source venv_st_latest/Scripts/activate  # activate venv on Linux
## via conda
$ conda create -n st
$ conda activate st

########### clone source and install dependent pkgs
$ git clone git@github.com:wgong/chat-records.git
$ cd chat-records
$ pip install -r requirements.txt

########### launch app
$ streamlit run app/Chat-Records.py
```

# Functionality

This app is built with streamlit web framework: 
- import chat-records from a saved HTML file;
- use beautifulsoup to parse the file;
- store question-and-answers in an SQLite database; 
- search and manage chat history using data-editor.

## Screenshots

- ![Welcome-to-Chat-Records](https://github.com/wgong/chat-records/blob/main/docs/screenshots/1-Chat-Records.png)
- ![Import-HTML-file](https://github.com/wgong/chat-records/blob/main/docs/screenshots/2-Import-HTML-file.png)
- ![Query-Chats](https://github.com/wgong/chat-records/blob/main/docs/screenshots/3-Query-Chats.png)
- ![Update-chat-record](https://github.com/wgong/chat-records/blob/main/docs/screenshots/4-Update-chat-record.png)

# Limitation


- On 2023-07-30, Claude started preventing one from saving chats as HTML file locally.
- On 2023-08-16, Claude allows saving chats as HTML file locally again.
- ChatGPT cannot be saved into a HTML file locally.