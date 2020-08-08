import os

import pandas as pd
from blob_storage import BlobStorageInterface
from const import TRAINING_CONTAINER, SCORING_CONTAINER, TRAINING_DATASTORE
from connect import AMLInterface
import psycopg2
from sklearn.model_selection import train_test_split


def read_df(csv_name):
    df=pd.read_csv(csv_name)
    X=df.drop(['class'],axis=1)
    y=df['class']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_val, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

    return X_train, y_train, X_val, y_val, X_test, y_test


def upload_training_data(BlobStorageInterface, X_train, y_train,X_val, y_val, X_test, y_test):
    BlobStorageInterface.upload_df_to_blob(
          X_train,
          TRAINING_CONTAINER,
          'train/X_train.csv'
    )
    BlobStorageInterface.upload_df_to_blob(
            y_train,
            TRAINING_CONTAINER,
            'train/y_train.csv'
        )

    BlobStorageInterface.upload_df_to_blob(
            X_test,
            TRAINING_CONTAINER,
            'test/X_test.csv'
        )
    BlobStorageInterface.upload_df_to_blob(
            y_test,
            TRAINING_CONTAINER,
            'test/y_test.csv'
        )
    BlobStorageInterface.upload_df_to_blob(
            X_valid,
            SCORING_CONTAINER,
            'X_valid.csv'
        )
    BlobStorageInterface.upload_df_to_blob(
            sy_valid,
            SCORING_CONTAINER,
            'y_valid.csv'
        )


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

    X_train, y_train, X_val, y_val, X_test, y_test = read_df('data.csv')
    
    upload_training_data(blob_storage_interface, X_train, y_train,X_val, y_val, X_test, y_test)

    aml_interface = AMLInterface(
        spn_credentials, subscription_id, workspace_name, resource_group
    )

    aml_interface.register_datastore(
        TRAINING_CONTAINER, TRAINING_DATASTORE,
        storage_acct_name, storage_acct_key
    )

if __name__ == '__main__':
    main()