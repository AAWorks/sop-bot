from utils.api_parser import FootAPIParser
import streamlit as st
import pandas as pd

PARSER = FootAPIParser()

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":soccer:")
st.title('Welcome to SOP Bot :gear:')
st.caption("A Proprietary Soccer Outcome Prediction Algorithm By Alejandro and Andres Alonso")
st.form()
country = st.text_input('Country')
next_input = st.submit()

if valid_country(country):
    st.text_input('League')

