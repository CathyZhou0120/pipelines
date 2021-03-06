from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from azureml.core import Datastore, Dataset, Run
import joblib
from sklearn.metrics import precision_score, recall_score
from const import TRAINING_DATASTORE, SCORING_CONTAINER, MODEL_NAME, AML_EXPERIMENT_NAME
import os 


__here__ = os.path.dirname(__file__)


def get_df_from_datastore_path(datastore, datastore_path):

    datastore_path = [(datastore, datastore_path)]
    dataset = Dataset.Tabular.from_delimited_files(
        path=datastore_path
    )
    dataframe = dataset.to_pandas_dataframe()
    return dataframe


def prepare_data(workspace):
    training_datastore = Datastore.get(workspace, TRAINING_DATASTORE)
    #validation_datastore = Datastore.get(workspace, SCORING_CONTAINER)
    x_train = get_df_from_datastore_path(training_datastore, 'train/X_train.csv')
    y_train = get_df_from_datastore_path(training_datastore, 'train/y_train.csv')
    y_train = y_train['class']
    x_test = get_df_from_datastore_path(training_datastore, 'valid/X_valid.csv')
    y_test = get_df_from_datastore_path(training_datastore, 'valid/y_valid.csv')
    y_test = y_test['class']
    return x_train, y_train, x_test, y_test

def evaluate_model(classifier, x_test, y_test, run):
    y_pred = classifier.predict(x_test)
    model_f1_score = f1_score(y_test, y_pred)
    p = precision_score(y_test, y_pred)
    r = recall_score(y_test, y_pred)
    run.log('F1_Score', model_f1_score)
    run.log('Precision_Score', p)
    run.log('Recall_Score', r)


def save_model(classifer,name):
    output_dir = os.path.join(__here__, 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, name)
    joblib.dump(classifer, model_path)
    run.log('model path',model_path)
    return model_path

def main():
    run = Run.get_context()
    workspace = run.experiment.workspace
    x_train, y_train, x_test, y_test = prepare_data(workspace)
    classifier = RandomForestClassifier(n_estimators=int(float(sys.argv[2])))
    classifier.fit(x_train, y_train)
    evaluate_model(classifier, x_test, y_test, run)
    model_path = save_model(classifier,'model.pkl' )
    return model_path



if __name__ == '__main__':
    main()
