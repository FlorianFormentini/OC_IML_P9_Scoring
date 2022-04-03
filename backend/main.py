"""https://testdriven.io/blog/fastapi-streamlit/
"""
import os
import uvicorn
import pandas as pd
import numpy as np
import joblib
import logging
from fastapi import (
    FastAPI,
    Path,
    HTTPException,
)  # , Body , UploadFile, File, HTTPException
from typing import List

from data_models import Client, PredictionOut


app = FastAPI(title="OC IML Bonus Project 01 - Scoring Model API")
logger = logging.getLogger("uvicorn.error")

THRESHOLD = 0.329

# load model and db
db = pd.read_csv("./cleaned_data.csv", index_col="SK_ID_CURR")
logger.info(f"✅ DB Loaded: {db.shape[1]} clients")
# load clf
clf = joblib.load("./best_clf.pkl")
logger.info(f"✅ Model Loaded: {clf['classifier'].__class__.__name__}")
# get output features of last step in each transformers
# trans == tuple('name', Pipeline, [input_cols])
cols_pp = [
    trans[1][-1].get_feature_names_out(input_features=trans[-1]).tolist()
    for trans in clf["preprocessor"].transformers_
]
# flatten list of lists
cols_pp = [item for sublist in cols_pp for item in sublist]


@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


@app.get("/clients/", response_model=List[Client])
def get_clients():
    clients = (
        db.reset_index()
        .replace(np.nan, 0)
        .to_dict(orient="records", into=Client.schema())
    )
    return clients


@app.post("/{idx}", response_model=PredictionOut)
async def predict(
    idx: int = Path(..., title="Client ID"),
    # data: ClientIn = Body(..., embed=False)
):
    if idx not in db.index:
        raise HTTPException(404, f"No client client with id {idx}")
    client_data = db[db.index == idx]
    # df = pd.DataFrame(data.dict(), index=[idx])
    # predict probability
    proba = clf.predict_proba(client_data)[:, 1][0]
    # apply threshold
    label = (proba >= THRESHOLD).astype("int")
    logger.info(f"Proba: {proba} - Label: {label}")
    # get preprocessed data
    client_data_pp = clf["preprocessor"].transform(client_data)
    return PredictionOut(
        proba=proba,
        label=label,
        features=client_data_pp.tolist(),
        features_name=cols_pp,
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0",
        # if $PORT: heroku else: docker-compose
        port=os.getenv("PORT", 8080)
    )
