import streamlit as st
import pandas as pd

from utils.parse import Dataset

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":gear:")
st.title('Welcome to SOP Bot :gear:')
st.caption("By Brothers Alejandro Alonso (AAWorks) and Andres Alonso (AXAStudio)")

st.info("SOP Bot is a sports outcome prediction bot with the goal of accurately predicting the outcome of upcoming soccer matches. SOP Bot utilizes two algorithms, a deep neural network and a gradient boosted decision tree.")

#@st.cache_data
def gen_data():
    raw = Dataset("mls")
    vis_raw = raw.peek()
    vis_aggregate = raw.aggregate_data(10)
    return vis_raw, vis_aggregate

pred, tfkeras, xgb, data = st.tabs(["Get Prediction :brain:", "Tensorflow/Keras Model :spider_web:", "XGBoost Model :evergreen_tree:", "View Dataset :page_facing_up:"])

with pred:
    st.info("Select a League and Upcoming Match to Predict")
with tfkeras:
    st.info("Tensorflow-keras Deep Neural Network Model")
with xgb:
    st.info("XGBoost Gradient Boosted Decision Tree")
with data:
    st.info("Raw, Aggregated, and Normalized Datasets")
    r, a = gen_data()
    st.dataframe(r)
    st.dataframe(a)
