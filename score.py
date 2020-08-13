# pylint: skip-file
import json


import numpy as np
from azureml.core.model import Model
import pickle 
from const import MODEL_NAME


def init():
    global model
    model_path = Model.get_model_path(MODEL_NAME)
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)


def run(data):
    try:
        data = json.loads(data)
        data = data['data']
        result = model.predict(np.array(data))
        return result.tolist()
    except Exception as e:
        error = str(e)
        return error