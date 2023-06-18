from utils.api_parser import FootAPIParser
import streamlit as st
import pandas as pd
import os

PARSER = FootAPIParser()

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":soccer:")
st.title('Welcome to SOP Bot :gear:')
st.caption("A Proprietary Soccer Outcome Prediction Algorithm By Alejandro and Andres Alonso")

#next_input = st.submit()
def valid_country(country):
    if country:
        return True

def valid_league(league):
    if league:
        return True

def valid_team(team):
    if team:
        return True
with st.form("Country"):
    st.text_input('Country')
    submitted = st.form_submit_button("To League")
    if submitted:
        st.text_input('League')
        next = st.form_submit_button("To Team")
        if next:
            st.text_input('Team')

        #next2 = st.form_submit_button("To Team")
    # Every form must have a submit button.
#    if next2:
#        

    
    

st.write("Outside the form")
