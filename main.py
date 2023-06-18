from utils.api_parser import FootAPIParser
import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":soccer:")
st.title('Welcome to SOP Bot :gear:')
st.caption("A Proprietary Soccer Outcome Prediction Algorithm By Alejandro and Andres Alonso")

with st.form("league"):
    league = st.text_input("League")
    userinput = st.form_submit_button("Continue")

if userinput:
    with st.form("teams"):
        home = st.text_input("Team 1")
        away = st.text_input('Team 2')
        predict = st.form_submit_button("Get Prediction")

if predict:
    st.write("working")
