# Chat-Records
Import and manage chat records with AI assistant like Claude, Bard


# Setup

Create a virtual env with the latest streamlit release

```
########### create venv
$ python -m venv venv_st_latest
$ venv_st_latest\Scripts\activate.bat     # activate venv on Windows
$ source venv_st_latest/Scripts/activate  # activate venv on Linux

########### clone source and install dependent pkgs
$ git clone git@github.com:wgong/chat-records.git
$ cd chat-records
$ pip install -r requirements.txt

########### launch app
$ streamlit run app/Home.py
```

# Architecture

This app is built with streamlit web framework: 
- import chat-records from a saved HTML file;
- use beautifulsoup to parse the file;
- store question-and-answers in an SQLite database; 
- search and manage chat history using data-editor.

# Limitation

It currently supports AI assistants like Claude, Bard. 

== An session from ChatGPT cannot be saved into a HTML file locally == (If you know how, please share.) 
