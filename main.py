import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":gear:")
st.title('Welcome to SOP Bot :gear:')
st.caption("By Brothers Alejandro Alonso (AAWorks) and Andres Alonso (AXAStudio)")

st.info("SOP Bot is a sports outcome prediction bot with the goal of accurately predicting the outcome of upcoming soccer matches. SOP Bot utilizes two algorithms, a deep neural network and a gradient boosted decision tree.")

pred, tfkeras, xgb, data = st.tabs(["Get Prediction :brain:", "Tensorflow/Keras Model :spider_web:", "XGBoost Model :evergreen_tree:", "View Dataset :page_facing_up:"])

with pred:
    st.info("Select a League and Upcoming Match to Predict")
with tfkeras:
    st.info("Tensorflow-keras Deep Neural Network Model")
with xgb:
    st.info("XGBoost Gradient Boosted Decision Tree")
with data:
    st.info("Raw, Aggregated, and Normalized Datasets")
