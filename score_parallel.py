import io
from sklearn.externals import joblib
import argparse
import numpy as np

from azureml.core.model import Model
from sklearn.ensemble import RandomForestClassifier


def init():
    global model
    model_path = Model.get_model_path('model.pkl')
    model = joblib.load(model_path)

def run(input_data):
    # make inference
    #num_rows, num_cols = input_data.shape
    pred = model.predict(input_data)

    # cleanup output
    result = input_data
    result['variety'] = pred

    return result