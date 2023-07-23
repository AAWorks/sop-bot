import streamlit as st
import pandas as pd

from utils.parse import Dataset
from tfx_algo import DNNModel

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":gear:")
st.title('Welcome to SOP Bot :gear:')
st.caption("By Brothers Alejandro Alonso (AAWorks) and Andres Alonso (AXAStudio)")

st.info("SOP Bot is a sports outcome prediction bot with the goal of accurately predicting the outcome of upcoming soccer matches. SOP Bot utilizes a live soccer API, an extensive amount of data processing, and a Tensorflow-Keras deep neural network.")

@st.cache_data
def preprocessing():
    data = Dataset("laligapremier")
    vis_raw = data.peek()

    agg_txt = "Processing Match Data (0% Complete)"
    #agg_bar = st.progress(0, text=agg_txt)
    vis_aggregate = data.aggregate_data(10)
    #agg_bar.progress(1.0, text="Done")

    vis_norm = data.normalize_aggregate(vis_aggregate)

    dnn_train = data.dnn_preprocessing(vis_norm, columns_to_drop=["fouls", "yellowcards", "redcards", "goalkeepersaves", "offsides", "longballs"], include_ties=False)
    return vis_raw, vis_aggregate, vis_norm, dnn_train

raw, agg, norm, records = preprocessing()

@st.cache_resource
def train_model(): 
    model = DNNModel(records)
    model.build()
    model.train()

    return model

tf_model = train_model()

pred, tfkeras, data = st.tabs(["Get Prediction :brain:", "Tensorflow/Keras Model :spider_web:", "Datasets :page_facing_up:"])

with pred:
    st.info("Select a League and Upcoming Match to Predict")
with tfkeras:
    st.info("Tensorflow-keras Deep Neural Network Model")
    history = tf_model.train_analytics()
    trainstat= tf_model.evaluate_train_on_confidence()
    st.write("Eval test")
    st.write(tf_model.evaluate_on_confidence())
    st.write("Eval test on Wins")
    st.write(tf_model.evaluate_on_confidence(1))
    st.write("Eval test on Losses")
    st.write(tf_model.evaluate_on_confidence(0))
    st.write("Eval on train")
    st.write(trainstat)
    st.write("Training Eval")
    st.line_chart(history['val_loss'])
    st.line_chart(history['val_accuracy'])
    st.line_chart(history['loss'])
    st.line_chart(history['accuracy'])
    prediction = tf_model.get_test_predictions()
    st.write("Test Preds")
    st.write(prediction)
with data:
    st.info("Raw, Aggregated, and Normalized Datasets")
    st.subheader("Preprocessed Data")
    st.dataframe(records)
    st.subheader("Normalized Aggregated Data")
    st.dataframe(norm)
    st.subheader("Aggregated Data")
    st.dataframe(agg)
    st.subheader("Raw Data")
    st.dataframe(raw)
    
    
