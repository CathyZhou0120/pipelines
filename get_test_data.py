import psycopg2
import csv
import os
from connect import AMLInterface
from azureml.core import Dataset

#conn_string = """dbname='exampledb' user='cathyzhou@cathydb2' host='cathydb2.postgres.database.azure.com' password='3.14159Zyr' port='5432' sslmode='require'"""
# Construct connection string


def get_data(host,user,dbname,password,port,sslmode,aml_interface):
    conn = psycopg2.connect(
        host=host,
    database=dbname,
    user=user,
    password=password,
    port=port,
    sslmode=sslmode
    ) 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM iris LIMIT 30;")
    rows = cursor.fetchall()

    with open('data.csv', 'w') as f:
        fieldnames = ['sepal_length', 'sepal_width','peta_length','petal_width','class']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in rows:
            writer.writerow({'sepal_length': i[0], 'sepal_width': i[1],'peta_length': i[2],'petal_width': i[3],'class': i[4]})
    
    datastore = aml_interface.workspace.get_default_datastore()
    datastore_paths = [(datastore, 'data.csv')]
    dataset = Dataset.Tabular.from_delimited_files(path=datastore_paths)
    dataset = dataset.register(workspace=aml_interface.workspace,
                                 name='example_data')
    

def main():
    dbname=os.environ['DBNAME']
    user=os.environ['DBUSER']
    host=os.environ['DBHOST']
    password=os.environ['DBPASSWORD']
    port=os.environ['DBPORT']
    sslmode=os.environ['DBSSL']
    #tenent_id=os.environ['TENANT_ID']
    resource_group = os.environ['RESOURCE_GROUP']
    subscription_id = os.environ['SUBSCRIPTION_ID']
    workspace_name = os.environ['AML_WORKSPACE_NAME']
    
    spn_credentials = {
        'tenant_id': os.environ['TENANT_ID'],
        'service_principal_id': os.environ['SPN_ID'],
        'service_principal_password': os.environ['SPN_PASSWORD'],
    }

    aml_interface = AMLInterface(
        spn_credentials, subscription_id, workspace_name, resource_group
    )
    #conn_string="""host={0} user={1} dbname={2} password={3} port={4} sslmode={5}""".format(host, user, dbname, password, port, sslmode)
    get_data(host,user,dbname,password,port,sslmode,aml_interface)
    #print(conn_string, tenent_id)


if __name__ == '__main__':
    main()