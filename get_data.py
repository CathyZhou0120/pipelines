import os

import pandas as pd
from blob_storage import BlobStorageInterface
from const import TRAINING_CONTAINER, SCORING_CONTAINER, TRAINING_DATASTORE
from connect import AMLInterface
from sklearn.model_selection import train_test_split



class get_data():
    def __init__(self):
        df=pd.read_csv('data.csv')
        ys=[]
        for i in df['class'].values:
            if i=='Iris-setosa':
                ys.append(0)
            else:
                ys.append(1)
        df['class']=ys
        X=df.drop(['class'],axis=1)
        y=df['class']
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.X_train, self.X_test, self.X_val, self.y_val = train_test_split(self.X_train, self.y_train, test_size=0.2, random_state=42)


    def upload_training_data(self, blob_storage):
        blob_storage.upload_df_to_blob(
          self.X_train,
          TRAINING_CONTAINER,
          'train/X_train.csv'
        )
        blob_storage.upload_df_to_blob(
            self.y_train,
            TRAINING_CONTAINER,
            'train/y_train.csv'
        )

        blob_storage.upload_df_to_blob(
            self.X_test,
            TRAINING_CONTAINER,
            'test/X_test.csv'
        )
        blob_storage.upload_df_to_blob(
            self.y_test,
            TRAINING_CONTAINER,
            'test/y_test.csv'
        )
        blob_storage.upload_df_to_blob(
            self.X_val,
            SCORING_CONTAINER,
            'X_valid.csv'
        )
        blob_storage.upload_df_to_blob(
            self.y_val,
            SCORING_CONTAINER,
            'y_valid.csv'
        )
    def upload_data(self, blob_storage):
        self.upload_training_data(blob_storage)


def main():
    storage_acct_name = os.environ['STORAGE_ACCT_NAME']
    storage_acct_key = os.environ['STORAGE_ACCT_KEY']
    workspace_name = os.environ['AML_WORKSPACE_NAME']
    resource_group = os.environ['RESOURCE_GROUP']
    subscription_id = os.environ['SUBSCRIPTION_ID']

    spn_credentials = {
        'tenant_id': os.environ['TENANT_ID'],
        'service_principal_id': os.environ['SPN_ID'],
        'service_principal_password': os.environ['SPN_PASSWORD'],
    }

    blob_storage_interface = BlobStorageInterface(
        storage_acct_name, storage_acct_key
    )

    data_creator = get_data()
    data_creator.upload_data(blob_storage_interface)

    aml_interface = AMLInterface(
        spn_credentials, subscription_id, workspace_name, resource_group
    )

    aml_interface.register_datastore(
        TRAINING_CONTAINER, TRAINING_DATASTORE,
        storage_acct_name, storage_acct_key
    )

if __name__ == '__main__':
    main()