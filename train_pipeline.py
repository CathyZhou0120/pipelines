trigger: none

schedules:
  - cron: "0 12 * * 0"
    displayName: "Weekly Sunday training pipeline run"
    branches:
      include:
      - master
    always: true

name: 'training_pipeline'
jobs:
  - job: 'training_pipeline_job'
    pool:
      vmImage: 'ubuntu-16.04'
    variables:
      - group: KeyVault
      - group: ProductionEnvVars
    steps:
      - task: UsePythonVersion@0
        inputs:
          versionSpec: '3.7.6'
          architecture: 'x64'
    
      - script: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        displayName: 'Install requirements'
    
      - script: |
          python create_aml_experiment.py
        displayName: 'Run AML Experiment and Register Model'
        env:
          TENANT_ID: $(TenantID)
          SPN_ID: $(SpnID)
          SPN_PASSWORD: $(SpnPassword)
          AML_WORKSPACE_NAME: $(AmlWorkspaceName)
          RESOURCE_GROUP: $(ResourceGroup)
          SUBSCRIPTION_ID: $(SubscriptionID)