import streamlit as st
st.set_page_config(layout="wide", page_title="SOP Bot", page_icon=":gear:")

from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.altex import sparkline_chart
from streamlit_extras.altex import hist_chart

import pandas as pd
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

from utils.parse import Dataset
from tfx_algo import DNNModel

AGGREGATION_DEPTH = 10
COLUMNS_TO_DROP = ["fouls", "yellowcards", "redcards", "goalkeepersaves", "offsides", "longballs"]

st.title('Welcome to SOP Bot :gear:')
st.caption("By Brothers Alejandro Alonso (AAWorks) and Andres Alonso (AXAStudio)")

st.info("SOP Bot is a sports outcome prediction bot with the goal of accurately predicting the outcome of upcoming soccer matches. SOP Bot utilizes a live soccer API, an extensive amount of data processing, and a Tensorflow-Keras deep neural network. Currently supports teams from the English Premier League and the Spanish La Liga. Cross-matchups are supported, although precision sees a ~7% increase in error.")

dataset = Dataset("laligapremier")

@st.cache_data
def preprocessing(_dataset):
    vis_raw = _dataset.peek()

    #agg_txt = "Processing Match Data (0% Complete)"
    #agg_bar = st.progress(0, text=agg_txt)
    vis_aggregate = _dataset.aggregate_data(AGGREGATION_DEPTH)
    #agg_bar.progress(1.0, text="Done")

    vis_norm = _dataset.normalize_aggregate(vis_aggregate)

    dnn_train = _dataset.dnn_preprocessing(vis_norm, columns_to_drop=COLUMNS_TO_DROP, include_ties=False)
    return vis_raw, vis_aggregate, vis_norm, dnn_train

raw, agg, norm, records = preprocessing(dataset)

@st.cache_resource
def train_model(): 
    model = DNNModel(records)
    model.build()
    model.train()

    return model

model = train_model()

@st.cache_resource
def generate_profile_report():
    return ProfileReport(records, minimal=True)

pr = generate_profile_report()

pred, tfkeras, preprocessed_dataset_profile, view_datasets = st.tabs(["Get Prediction :brain:", "Model Analytics :spider_web:", "Processed Dataset Profile Report :mag:", "View Base Dataset :page_facing_up:"])

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
        historical_statistics = dataset.potential_match_preprocessing(agg, home_team, away_team, AGGREGATION_DEPTH, COLUMNS_TO_DROP)
        historical_statistics.drop("result", axis=1, inplace=True)
        probability, prediction = model.pretty_prediction(historical_statistics, home_team, away_team)
        if 0.45 < probability < 0.55 : st.warning(prediction)
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
    st.info("Tensorflow/Keras Deep Neural Network Model Summary & Evaluation Metrics")
    st.code(model.summary(), language='python')
    # st.divider()
    history = model.train_analytics()
    trainstat = model.evaluate_train_on_confidence()
    # col1, col2, col3, col4 = st.columns(4)
    # val_acc = round(model.evaluate_on_confidence() * 100, 2)
    # loss_acc = round(model.evaluate_on_confidence(0) * 100, 2)
    # win_acc = round(model.evaluate_on_confidence(1) * 100, 2)
    train_acc = round(model.evaluate_train_on_confidence() * 100, 2)
    # col1.metric(label="Testing Accuracy", value=f"{val_acc}%", delta=f"{round(val_acc - 50, 2)}%")
    # col2.metric(label="Testing Accuracy (Wins)", value=f"{win_acc}%", delta=f"{round(win_acc - 50, 2)}%")
    # col3.metric(label="Testing Accuracy (Losses)", value=f"{loss_acc}%", delta=f"{round(loss_acc - 50, 2)}%")
    # col4.metric(label="Training Accuracy", value=f"{train_acc}%", delta=f"{round(train_acc - 50, 2)}%")
    style_metric_cards()

    st.divider()
    testloss, testacc, trainloss, trainacc = st.columns(4)
    with testloss:
        data = pd.DataFrame()
        data['val_loss'] = history['val_loss']
        data['epoch'] = list(range(data.shape[0]))
        st.metric("Validation Loss", str(data["val_loss"].min())[:6])
        sparkline_chart(
            data=data,
            x="epoch",
            y="val_loss:Q",
            height=80,
            autoscale_y=True,
        )
    with testacc:
        data = pd.DataFrame()
        data['val_accuracy'] = history['val_precision']
        data['epoch'] = list(range(data.shape[0]))
        st.metric("Validation Precision", str(data["val_accuracy"].max() * 100)[:5] + "%", delta=f"{round(data['val_accuracy'].max() * 100 - 50, 2)}%")
        sparkline_chart(
            data=data,
            x="epoch",
            y="val_accuracy:Q",
            height=80,
            autoscale_y=True,
        )
    with trainloss:
        data = pd.DataFrame()
        data['loss'] = history['loss']
        data['epoch'] = list(range(data.shape[0]))
        st.metric("Training Loss", str(data["loss"].min())[:6])
        sparkline_chart(
            data=data,
            x="epoch",
            y="loss:Q",
            height=80,
            autoscale_y=True,
        )
    with trainacc:
        data = pd.DataFrame()
        data['accuracy'] = history['precision']
        data['epoch'] = list(range(data.shape[0]))
        st.metric("Training Precision", str(train_acc) + "%", delta=f"{round(data['accuracy'].max() * 100 - 50, 2)}%")
        sparkline_chart(
            data=data,
            x="epoch",
            y="accuracy:Q",
            height=80,
            autoscale_y=True,
        )
    # st.line_chart(history['val_loss']) #NEEDS BETTER IMPLEMENTATION
    # st.line_chart(history['val_accuracy'])
    # st.line_chart(history['loss'])
    # st.line_chart(history['accuracy'])
    st.divider()
    predictions = model.get_test_predictions() * 100
    prediction_df = pd.DataFrame()
    prediction_df["probability"] = predictions.astype(int).tolist()
    hist_chart(
        data=prediction_df,
        x="probability",
        title="Distribution of Outputted Test Set Probabilities"
    )

with preprocessed_dataset_profile:
    st.info("Profile Report on the Utilized Dataset (Post Processing)")
    if pr:
        st_profile_report(pr)

with view_datasets:
    st.info("Base Dataset - Pulled Directly from FootAPI")
    data = pd.DataFrame(raw)
    filtered_df = dataframe_explorer(data)
    st.dataframe(filtered_df, use_container_width=True) 
