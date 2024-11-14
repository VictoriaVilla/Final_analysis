import streamlit as st

def menu():
    css = '''
    <style>
        .stMainBlockContainer {max-width:75rem}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("home-page.py", label="Home", icon=":material/home:")
    st.sidebar.page_link("pages/files-page.py", label="Files", icon=":material/folder_open:")
    st.sidebar.page_link("pages/analysis-page.py", label="Analysis", icon=":material/monitoring:")
    st.sidebar.page_link("pages/reports-page.py", label="Reports", icon=":material/summarize:")
    st.sidebar.page_link("pages/help-page.py", label="Help", icon=":material/help:")