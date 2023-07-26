import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.dataframe_explorer import dataframe_explorer

from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

from utils.parse import Dataset
from tfx_algo import DNNModel

AGGREGATION_DEPTH = 10
COLUMNS_TO_DROP = ["fouls", "yellowcards", "redcards", "goalkeepersaves", "offsides", "longballs"]

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
    st.info("Tensorflow-keras Deep Neural Network Model")
    add_vertical_space(1)
    history = model.train_analytics()
    trainstat = model.evaluate_train_on_confidence()
    col1, col2, col3, col4 = st.columns(4)
    val_acc = round(model.evaluate_on_confidence() * 100, 2)
    loss_acc = round(model.evaluate_on_confidence(0) * 100, 2)
    win_acc = round(model.evaluate_on_confidence(1) * 100, 2)
    train_acc = round(model.evaluate_train_on_confidence() * 100, 2)
    col1.metric(label="Testing Accuracy", value=val_acc, delta=round(val_acc - 50, 2))
    col2.metric(label="Testing Accuracy (Wins)", value=win_acc, delta=round(win_acc - 50, 2))
    col3.metric(label="Testing Accuracy (Losses)", value=loss_acc, delta=round(loss_acc - 50, 2))
    col4.metric(label="Train Accuracy", value=train_acc, delta=round(train_acc - 50, 2))
    style_metric_cards()

    st.line_chart(history['val_loss'])
    st.line_chart(history['val_accuracy'])
    st.line_chart(history['loss'])
    st.line_chart(history['accuracy'])
    prediction = model.get_test_predictions()
    st.write("Test Preds")
    st.write(prediction)

with preprocessed_dataset_profile:
    if pr:
        st_profile_report(pr)

with view_datasets:
    st.info("Base Dataset - Pulled directly from FootAPI")
    filtered_df = dataframe_explorer(raw, case=False)
    st.dataframe(filtered_df, use_container_width=True) 
