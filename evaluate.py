from azureml.core import ScriptRunConfig, Experiment, Environment
from connect import AMLInterface
from azureml.core.model import Model
from azureml.core import Run
import re
import os 
from const import (
    AML_COMPUTE_NAME, AML_ENV_NAME, AML_EXPERIMENT_NAME)


def get_experiment(aml_interface,AML_EXPERIMENT_NAME):
    experiment=Experiment(workspace=aml_interface.workspace, name=AML_EXPERIMENT_NAME)
    return experiment


def evaluate(experiment,metric):
    max_f1_runid = None
    max_f1 = None

    for run in experiment.get_runs():
        run_metrics = run.get_metrics()
        run_details = run.get_details()
    
        try:
            run_f1=run_metrics[metric]
            run_id = run_details['runId']
    
            if max_f1 is None:
                max_f1=run_f1
                max_run_id = run_id
            else:
                if run_f1 > max_f1:
                    max_f1=run_f1
                    max_run_id=run_id
        except:
            pass
    return max_run_id

def register_model(run_id,experiment):
    best_run = Run(experiment=experiment, run_id=run_id)
    files = best_run.get_file_names()
    r = re.compile('outputs.*')
    model_path = [l for l in files if r.match(l)]
    path,model = os.path.split(model_path[0])

    model = best_run.register_model(model_name = model, model_path = path)
    return path


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

    experiment=get_experiment(aml_interface,AML_EXPERIMENT_NAME)
    run_id = evaluate(experiment,'F1_Score')
    register_model(run_id,experiment)

if __name__ == '__main__':
    main()

    
