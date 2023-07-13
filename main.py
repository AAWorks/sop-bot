import streamlit as st

from utils.parse import Dataset
from tfx_algo import DNNModel

st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":gear:")
st.title('Welcome to SOP Bot :gear:')
st.caption("By Brothers Alejandro Alonso (AAWorks) and Andres Alonso (AXAStudio)")

st.info("SOP Bot is a sports outcome prediction bot with the goal of accurately predicting the outcome of upcoming soccer matches. SOP Bot utilizes two algorithms, a deep neural network and a gradient boosted decision tree.")

@st.cache_data
def get_and_parse():
    raw = Dataset("mls")
    vis_raw = raw.peek()

    agg_txt = "Aggregating Data (0% Complete)"
    agg_bar = st.progress(0, text=agg_txt)
    vis_aggregate = raw.aggregate_data(10, agg_bar)

    norm_txt = "Normalizing Data (0% Complete)"
    norm_bar = st.progress(0, text=norm_txt)
    vis_norm = raw.normalize_aggregate(vis_aggregate, norm_bar)
    return vis_raw, vis_aggregate, vis_norm

raw, agg, norm = get_and_parse()

@st.cache_resource
def get_tf_model():
    model = DNNModel(norm)
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
    st.line_chart(history['acc'])
with xgb:
    st.info("XGBoost Gradient Boosted Decision Tree")
with data:
    st.info("Raw, Aggregated, and Normalized Datasets")
    st.subheader("Raw Data")
    st.dataframe(raw)
    st.subheader("Aggregated Data")
    st.dataframe(agg)
    st.subheader("Normalized Aggregated Data")
    st.dataframe(norm)
