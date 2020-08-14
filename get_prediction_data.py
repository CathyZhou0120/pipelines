import psycopg2
import csv
import os

from azureml.core.dataset import Dataset
from azureml.core.datastore import Datastore
from connect import AMLInterface 
from const import PREDICTION_FILE, PREDICTION_PATH, TARGET_PATH, PREDICTION_DATASET_NAME

__here__ = os.path.dirname(__file__)

def get_data(host,user,dbname,password,port,sslmode):
    conn = psycopg2.connect(
        host=host,
    database=dbname,
    user=user,
    password=password,
    port=port,
    sslmode=sslmode
    ) 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM iris LIMIT 20;")
    rows = cursor.fetchall()

    
    filename = os.path.join(__here__, '/', PREDICTION_FILE)
    with open(filename, 'w') as f:
        fieldnames = ['sepal_length', 'sepal_width','peta_length','petal_width','class']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in rows:
            writer.writerow({'sepal_length': i[0], 'sepal_width': i[1],'peta_length': i[2],'petal_width': i[3],'class': i[4]})


def register_dataset(aml_interface):
    datastore = aml_interface.workspace.get_default_datastore()

    src_dir = os.path.join(__here__, '/', PREDICTION_PATH)
    target_path = os.path.join(__here__, '/', TARGET_PATH)
    #datastore.upload(src_dir=src_dir, target_path=target_path,overwrite=True)   

    #dataset = Dataset.Tabular.from_delimited_files(datastore.path(PREDICTION_FILE))
    #dataset = dataset.register(workspace=aml_interface.workspace,
     #                            name=PREDICTION_DATASET_NAME)
    return src_dir,target_path

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
    register_dataset(aml_interface)

if __name__ == '__main__':
    main()
