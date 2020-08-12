from sklearn.ensemble import RandomForestClassifier
from azureml.core import Datastore, Dataset, Run
import joblib
from azureml.core.model import Model
from const import TRAINING_DATASTORE, MODEL_NAME, MODEL_VERSION


def get_df_from_datastore_path(datastore, datastore_path):
    # In our example we only have single files,
    # but these may be daily data dumps
    datastore_path = [(datastore, datastore_path)]
    dataset = Dataset.Tabular.from_delimited_files(
        path=datastore_path
    )
    dataframe = dataset.to_pandas_dataframe()
    return dataframe


def prepare_data(workspace):
    datastore = Datastore.get(workspace, TRAINING_DATASTORE)
    x_test = get_df_from_datastore_path(datastore, 'train/X_test.csv')
    y_test = get_df_from_datastore_path(datastore, 'train/y_test.csv')
    y_test = y_test['class']
    return x_test, y_test

def get_model():
    global model 
    model = Model(ws, name=MODEL_NAME)

    
