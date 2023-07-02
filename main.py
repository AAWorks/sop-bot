from utils.api_search import FootAPISearch
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":soccer:")
st.title('Welcome to SOP Bot :gear:')
st.caption("A Proprietary Soccer Outcome Prediction Algorithm By Alejandro and Andres Alonso")

predict, userinput = False, False
accepted_leagues = ["mls"]
with st.form("league"):
    league = st.text_input("League").lower().strip().replace(" ", "-")
    userinput = st.form_submit_button("Enter")

if league:
    if not(league in accepted_leagues):
        st.error('League not registered', icon="🚨")
    else:
        with st.form("teams"):
            home = st.text_input("Team 1")
            away = st.text_input('Team 2')
            predict = st.form_submit_button("Get Prediction")

        if home and away:
            st.success("working")
