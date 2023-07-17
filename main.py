import streamlit as st
import pandas as pd

from utils.parse import Dataset
from tfx_algo import DNNModel

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":gear:")
st.title('Welcome to SOP Bot :gear:')
st.caption("By Brothers Alejandro Alonso (AAWorks) and Andres Alonso (AXAStudio)")

st.info("SOP Bot is a sports outcome prediction bot with the goal of accurately predicting the outcome of upcoming soccer matches. SOP Bot utilizes two algorithms, a deep neural network and a gradient boosted decision tree.")

@st.cache_data
def preprocessing():
    data = Dataset("mls")
    vis_raw = data.peek()

    agg_txt = "Processing Match Data (0% Complete)"
    agg_bar = st.progress(0, text=agg_txt)
    vis_aggregate = data.aggregate_data(10, agg_bar)
    agg_bar.progress(1.0, text="Done")

    vis_norm = data.normalize_aggregate(vis_aggregate)

    dnn_train = data.dnn_preprocessing(vis_norm, columns_to_drop=["shotsinsidebox", "goalkeepersaves", "cornerkicks", "offsides", "fouls", "yellowcards", "redcards", "longballs", "crosses", "interceptions", "clearances"])
    return vis_raw, vis_aggregate, vis_norm, dnn_train

raw, agg, norm, records = preprocessing()

#@st.cache_resource
def get_tf_model(): 
    # a, b, c = records.loc[records['result'] == 0], records.loc[records['result'] == 1], records.loc[records['result'] == 2]
    # st.write(a.shape[0])
    # st.write(b.shape[0])
    # st.write(c.shape[0])
    # b = b.head(500).reset_index()
    # a = a.head(500).reset_index()
    # c = c.head(500).reset_index()
    # tmp = pd.concat([a, b]).sort_index(kind='merge')
    # tmp = tmp.drop("index", axis=1).drop("home_score", axis=1).drop("away_score", axis=1).drop("home_ties", axis=1).drop("away_ties", axis=1).drop("home_losses", axis=1).drop("away_losses", axis=1)
    # st.write(tmp)
    model = DNNModel(records)
    model.build()
    model.train()

    return model

tf_model = get_tf_model()

pred, tfkeras, xgb, data = st.tabs(["Get Prediction :brain:", "Tensorflow/Keras Model :spider_web:", "XGBoost Model :evergreen_tree:", "Datasets :page_facing_up:"])

with pred:
    st.info("Select a League and Upcoming Match to Predict")
with tfkeras:
    st.info("Tensorflow-keras Deep Neural Network Model")
    history = tf_model.train_analytics()
    stats = tf_model.evaluate()
    st.write(stats)
    st.line_chart(history['loss'])
    st.line_chart(history['accuracy'])
    prediction = tf_model.get_test_predictions()
    st.write(prediction)
with xgb:
    st.info("XGBoost Gradient Boosted Decision Tree")
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
    
    
