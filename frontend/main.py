import os
import requests
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import joblib
import shap


def st_shap(plot, height=None):
    div_style = "background-color: white;border-radius: 5px;"
    shap_html = f"<head>{shap.getjs()}</head><body><div style='{div_style}'>{plot.html()}</div></body>"  # noqa
    components.html(shap_html, height=height)


# if env vars: heroku else: local docker-compose
BACKEND_HOST = os.getenv("BACKEND_HOST", "http://backend:8080")
BACKEND_PORT = os.getenv("BACKEND_PORT", 8080)

# load model explainer
explainer = joblib.load("./shap_explainer.pkl")

# set page config
st.set_page_config(
    page_title="OC IML BP1 - Scoring Model",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="auto",
)

# page title
st.title("Scoring Model Web App")
st.caption("OC IML - Bonus Project 01")

# req to get db data
with st.spinner(text="Accessing DB ..."):
    r_all = requests.get(f"{BACKEND_HOST}/clients/")
try:
    r_all.raise_for_status()
    df = pd.DataFrame(r_all.json()).set_index("SK_ID_CURR")
    st.dataframe(df)

    st.markdown("### Prediction :")
    # SK_ID_CURR selection
    options = ["< Client ID >"] + list(df.index.values)
    # options = df.index.values.tolist()
    client_id = st.selectbox("Select client ID", options)

    if client_id and client_id != options[0]:
        # req to backend with spinner
        with st.spinner(text="Predictions in progress..."):
            r_client = requests.post(f"{BACKEND_HOST}/{client_id}")

        r_client.raise_for_status()
        preds = r_client.json()
        # display result
        # st.success("Predictions obtained !")
        # st.balloons()
        col1, col2, col3 = st.columns(3)
        msg = f"{preds['proba']*100:.2f}% {'❌' if preds['label'] else '✅'}"
        col2.metric(label="Payment failure probability:", value=msg)
        col3.write("Threshold: 32,9 %")

        # compute shap_values with client data
        features = np.array(preds["features"])
        shap_values = explainer.shap_values(features)
        # load cols_pp
        # force plot
        st_shap(
            shap.force_plot(
                explainer.expected_value,
                shap_values[0, :],
                features=features,
                feature_names=preds["features_name"],
            ),
            height=170,  # html iframe height
        )
        st.markdown("### Client's data")
        st.dataframe(df[df.index == client_id].T.astype(str))

except requests.exceptions.HTTPError as e:
    st.error(e)
except FileNotFoundError as e:
    st.error(f"File not found: {e}")
