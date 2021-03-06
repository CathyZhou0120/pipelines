import psycopg2
import csv
import os
from blob_storage import BlobStorageInterface
from azureml.core.dataset import Dataset
from azureml.core.datastore import Datastore
from connect import AMLInterface 
from const import PREDICTION_FILE, PREDICTION_PATH, TARGET_PATH, PREDICTION_DATASET_NAME

__here__ = os.path.dirname(__file__)
filename = os.path.join(__here__, '/', PREDICTION_FILE)

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
    cursor.execute("SELECT sepal_length, sepal_width, peta_length, petal_width FROM iris LIMIT 20;")
    rows = cursor.fetchall()

    
    #filename = os.path.join(__here__, '/', PREDICTION_FILE)
    with open('data_new.csv', 'w') as f:
        fieldnames = ['sepal_length', 'sepal_width','peta_length','petal_width']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in rows:
            writer.writerow({'sepal_length': i[0], 'sepal_width': i[1],'peta_length': i[2],'petal_width': i[3]})


#def register_dataset(aml_interface):
    #datastore = aml_interface.workspace.get_default_datastore()

    #src = os.path.join(__here__, '/', PREDICTION_PATH)
    #target_path = os.path.join(__here__, '/', TARGET_PATH)
    #datastore.upload_files(files = ['./data_new.csv'], target_path='testdata/',overwrite=True,show_progress = True)   
    #datastore_paths = [(datastore, 'testdata/data_new.csv')]
    #dataset = Dataset.Tabular.from_delimited_files(path=datastore_paths)
    #dataset = dataset.register(workspace=aml_interface.workspace,
    #                             name=PREDICTION_DATASET_NAME)
    #return src_dir,target_path

def upload_prediction_to_container(blob_storage):
    blob_storage.upload_csv_to_blob(
          'data_new.csv',
          'prediction',
          'data_new.csv'
        )

def upload_data(blob_storage):
    upload_prediction_to_container(blob_storage)

def register_dataset(path,aml_interface,storage_acct_name,storage_acct_key):
    workspace= aml_interface.workspace
    datastore = Datastore.register_azure_blob_container(workspace=workspace, 
                                                         datastore_name='prediction', 
                                                         container_name='prediction', 
                                                         account_name=storage_acct_name,
                                                         account_key=storage_acct_key)

    prediction_datastore = Datastore.get(workspace, 'prediction')
    datastore_path = [(prediction_datastore, path)]
    dataset = Dataset.Tabular.from_delimited_files(
        path=datastore_path
    )
    dataset = dataset.register(workspace=aml_interface.workspace,
                                 name='Prediction')
    


def main():
    storage_acct_name = os.environ['STORAGE_ACCT_NAME']
    storage_acct_key = os.environ['STORAGE_ACCT_KEY']
    workspace_name = os.environ['AML_WORKSPACE_NAME']
    resource_group = os.environ['RESOURCE_GROUP']
    subscription_id = os.environ['SUBSCRIPTION_ID']

    dbname=os.environ['DBNAME']
    user=os.environ['DBUSER']
    host=os.environ['DBHOST']
    password=os.environ['DBPASSWORD']
    port=os.environ['DBPORT']
    sslmode=os.environ['DBSSL']

    spn_credentials = {
        'tenant_id': os.environ['TENANT_ID'],
        'service_principal_id': os.environ['SPN_ID'],
        'service_principal_password': os.environ['SPN_PASSWORD'],
    }

    blob_storage_interface = BlobStorageInterface(
        storage_acct_name, storage_acct_key
    )

    aml_interface = AMLInterface(
        spn_credentials, subscription_id, workspace_name, resource_group
    )

    get_data(host,user,dbname,password,port,sslmode)
    upload_data(blob_storage_interface)
    register_dataset('data_new.csv',aml_interface,storage_acct_name,storage_acct_key)

if __name__ == '__main__':
    main()
