import streamlit as st
import pandas as pd
import numpy as np
from menu import menu

st.set_page_config(layout="centered")

menu()

st.title('Narre Warren South Traffic Project')
st.write("This site offers interactive reports on the analysis  of imported data collected from the area surrounding Warren South P-12 College")
if st.button("Get Started", type="primary"):
    st.switch_page("pages\\files-page.py")
