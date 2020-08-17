from azureml.core.dataset import Dataset
from azureml.core.datastore import Datastore
from connect import AMLInterface 
from const import PREDICTION_FILE,PREDICTION_DATASET_NAME,PARALLEL_TASK_NAME,COMPUTE_NAME
from azureml.pipeline.core import PipelineData
from azureml.core import Environment
from azureml.core.runconfig import CondaDependencies
from azureml.contrib.pipeline.steps import ParallelRunStep, ParallelRunConfig
from azureml.core import Experiment
from azureml.pipeline.core import Pipeline
import os

def get_test_data(aml_interface):
    datastore = aml_interface.workspace.get_default_datastore()
    datastore_paths = [(datastore, PREDICTION_FILE)]
    dataset = Dataset.Tabular.from_delimited_files(path=datastore_paths)

    registered_iris_ds= dataset.register(workspace=aml_interface.workspace,
                                 name=PREDICTION_DATASET_NAME,create_new_version=True)
    named_iris_ds = registered_iris_ds.as_named_input(PREDICTION_DATASET_NAME)

    output_folder = PipelineData(name=PARALLEL_TASK_NAME, datastore=datastore)
    return named_iris_ds,output_folder


def set_env():
    predict_conda_deps = CondaDependencies.create(pip_packages=["scikit-learn==0.22.1",
                                                            "azureml-core", "azureml-dataset-runtime[pandas,fuse]"])

    predict_env = Environment(name="predict_environment")
    predict_env.python.conda_dependencies = predict_conda_deps
    predict_env.docker.enabled = True
    predict_env.spark.precache_packages = False
    return predict_env


def run_parallel(distributed_csv_iris_step,aml_interface):
    ws = aml_interface.workspace
    pipeline = Pipeline(workspace=ws, steps=[distributed_csv_iris_step])   
    pipeline_run = Experiment(ws, 'iris-prs').submit(pipeline) 
    pipeline_run.wait_for_completion(show_output=True)


def main():
    workspace_name = os.environ['AML_WORKSPACE_NAME']
    resource_group = os.environ['RESOURCE_GROUP']
    subscription_id = os.environ['SUBSCRIPTION_ID']

    spn_credentials = {
        'tenant_id': os.environ['TENANT_ID'],
        'service_principal_id': os.environ['SPN_ID'],
        'service_principal_password': os.environ['SPN_PASSWORD'],
    }

    aml_interface = AMLInterface(
        spn_credentials, subscription_id, workspace_name, resource_group
    )

    dataset,output_folder=get_test_data(aml_interface)
    predict_env = set_env()

    compute_target = aml_interface.workspace.compute_targets[COMPUTE_NAME]


    parallel_run_config = ParallelRunConfig(
    source_directory='.',
    entry_script='score_parallel.py',  
    mini_batch_size='5MB',
    error_threshold=1,
    output_action='append_row',
    append_row_file_name="iris_outputs_new.txt",
    environment=predict_env,
    compute_target=compute_target, 
    node_count=1,
    run_invocation_timeout=600)

    distributed_csv_iris_step = ParallelRunStep(
    name='example-iris',
    inputs=[dataset],
    output=output_folder,
    parallel_run_config=parallel_run_config,
    #arguments=['--model_name', 'model_new.pkl'],
    allow_reuse=True)
 
    run_parallel(distributed_csv_iris_step,aml_interface)


if __name__ == '__main__':
    main()


