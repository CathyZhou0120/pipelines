import os

from azureml.core.environment import Environment
from azureml.core.model import InferenceConfig, Model
from azureml.core.webservice import AciWebservice, Webservice

from connect import AMLInterface
from const import (
    AML_ENV_NAME, DEPLOYMENT_SERVICE_NAME, MODEL_NAME)


__here__ = os.path.dirname(__file__)


def deploy(aml_interface,inference_config,service_name):
    inference_config = inference_config
    aci_config = AciWebservice.deploy_configuration(
        cpu_cores=1,
        memory_gb=1
    )
    model = aml_interface.workspace.models.get(MODEL_NAME)

    service = Model.deploy(
        aml_interface.workspace,
        name=service_name,
        models=[model],
        inference_config=inference_config,
        deployment_config=aci_config)
    service.wait_for_deployment(show_output=True)
    print(service.scoring_uri)


def main(inference_config,service_name):
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
    #webservices = aml_interface.workspace.webservices.keys()
    
    deploy(aml_interface,inference_config,service_name)



if __name__ == '__main__':

    service_name = 'aml-pipeline-deploy'

    scoring_script_path = os.path.join(__here__, 'score.py')
    aml_env = Environment.get(
        workspace=aml_interface.workspace,
        name=AML_ENV_NAME
    )
    inference_config = InferenceConfig(entry_script=scoring_script_path, environment=aml_env)

    main(inference_config,service_name)
