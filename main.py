import streamlit as st
import pandas as pd
import time
import random

from utils.parse import Dataset
from tfx_algo import DNNModel

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":gear:")
st.title('Welcome to SOP Bot :gear:')
st.caption("By Brothers Alejandro Alonso (AAWorks) and Andres Alonso (AXAStudio)")

st.info("SOP Bot is a sports outcome prediction bot with the goal of accurately predicting the outcome of upcoming soccer matches. SOP Bot utilizes a live soccer API, an extensive amount of data processing, and a Tensorflow-Keras deep neural network.")

dataset = Dataset("laligapremier")

@st.cache_data
def preprocessing(_dataset):
    vis_raw = _dataset.peek()

    #agg_txt = "Processing Match Data (0% Complete)"
    #agg_bar = st.progress(0, text=agg_txt)
    vis_aggregate = _dataset.aggregate_data(10)
    #agg_bar.progress(1.0, text="Done")

    vis_norm = _dataset.normalize_aggregate(vis_aggregate)

    dnn_train = _dataset.dnn_preprocessing(vis_norm, columns_to_drop=["fouls", "yellowcards", "redcards", "goalkeepersaves", "offsides", "longballs"], include_ties=False)
    return vis_raw, vis_aggregate, vis_norm, dnn_train

raw, agg, norm, records = preprocessing(dataset)

@st.cache_resource
def train_model(): 
    model = DNNModel(records)
    model.build()
    model.train()

    return model

model = train_model()

pred, tfkeras, datasets = st.tabs(["Get Prediction :brain:", "Tensorflow/Keras Model :spider_web:", "Datasets :page_facing_up:"])


with pred:
    teamnames = dataset.team_names
    st.info("Predict a Match Outcome")

    col1, col2 = st.columns(2)
    # select team 1
    home_team = col1.selectbox(
    'Home Team',
    teamnames) 

    # select team 2
    away_team = col2.selectbox(
    'Away Team',
    teamnames)

    if home_team == away_team:
        submitted = st.button("Generate Prediction", disabled=True, use_container_width=True)
    else:
        submitted = st.button("Generate Prediction", disabled=False, use_container_width=True)
    
    if submitted:
        match_aggregate = []
        probability, prediction = model.pretty_prediction(match_aggregate, home_team, away_team)
        if 0.40 < probability < 0.60 : st.warning(prediction)
        else: st.success(prediction)
        # if submitted:
        #     if home_team == away_team:
        #         st.warning("Please select 2 different teams")
        #     else:
        #         st.success("Submitted to the AI :brain:")
        #         done = True
    # if done:
    #     with st.spinner('Asking the AI'):
    #         ask_ai(home_team,away_team)

with tfkeras:
    st.info("Tensorflow-keras Deep Neural Network Model")
    history = model.train_analytics()
    trainstat= model.evaluate_train_on_confidence()
    st.write("Eval test")
    st.write(model.evaluate_on_confidence())
    st.write("Eval test on Wins")
    st.write(model.evaluate_on_confidence(1))
    st.write("Eval test on Losses")
    st.write(model.evaluate_on_confidence(0))
    st.write("Eval on train")
    st.write(trainstat)
    st.write("Training Eval")
    st.line_chart(history['val_loss'])
    st.line_chart(history['val_accuracy'])
    st.line_chart(history['loss'])
    st.line_chart(history['accuracy'])
    prediction = model.get_test_predictions()
    st.write("Test Preds")
    st.write(prediction)
with datasets:
    st.info("Raw, Aggregated, and Normalized Datasets")
    st.subheader("Preprocessed Data")
    st.dataframe(records)
    st.subheader("Normalized Aggregated Data")
    st.dataframe(norm)
    st.subheader("Aggregated Data")
    st.dataframe(agg)
    st.subheader("Raw Data")
    st.dataframe(raw)
    
    
