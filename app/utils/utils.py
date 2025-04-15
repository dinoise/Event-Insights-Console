# App context
from flask import current_app

# Timezone control
from pytz import timezone

# Tools for better logging
from google.cloud import logging as cloud_logging
from logging import getLogger, ERROR

# secretmanager: Library to retrieve secret variables within GCP.
# storage: Library that allows access to GCP storage buckets.
from google.cloud import secretmanager, bigquery

from os import getenv

# Mexico City timezone
CDMX_TZ = timezone('America/Mexico_City')
"""
Constant representing the Mexico City (CDMX) timezone using `pytz` timezone format.

Usage:
------
Used to standardize timestamps in processes related to logs and records.

Example:
--------
fecha_hora = datetime.now().astimezone(CDMX_TZ)
"""

BQ_CLIENT = bigquery.Client()
"""
BQ_CLIENT is an instance of `google.cloud.bigquery.Client` used to interact with Google BigQuery.

This client allows executing queries, inserting data, managing datasets, and performing other 
operations within a Google Cloud BigQuery project.

Usage Example:
```
    query_job = BQ_CLIENT.query("SELECT * FROM dataset.table")
    results = query_job.result()  # Fetch query results
```
"""

# Initialize Google Cloud Logging client
LOG_CLIENT = cloud_logging.Client()
"""
Google Cloud Logging client.

Description:
------------
This client is used to send logs from the application to the Google Cloud Logging explorer, 
allowing centralized monitoring and visualization of event and error logs.
"""
LOG_CLIENT.setup_logging()  # Redirects Python logs to Google Cloud Logging

# Configure the logger. This is used to create error logs within Google Cloud.
LOGGER = getLogger()
"""
Python logger configured to report errors.

Description:
------------
This variable uses Python’s `logging` module to create a logger that manages error logs.
The logger is set to record only messages with `ERROR` level or higher.
"""
LOGGER.setLevel(ERROR)

# Initialize the Secrets client
SECRET_CLIENT = secretmanager.SecretManagerServiceClient()
"""
Google Cloud Secret Manager client.

Description:
------------
This client is used to access Google Cloud Secret Manager, allowing retrieval of secrets 
such as passwords, tokens, and other credentials that need to be securely stored.
"""

def get_secret(secret_name: str) -> str:
    """
    Retrieves the value of a secret stored in Google Cloud Secret Manager.

    Args:
        secret_name (str):Name of the secret in Google Cloud Secret Manager.

    Returns:
        str: Value of the requested secret.
    """

    project_id = getenv("GOOGLE_CLOUD_PROJECT")
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    try:
        response = SECRET_CLIENT.access_secret_version(name=name)
    except Exception as e:
        print(f"Error retrieving the secret from GCP: {e}")
        raise Exception(e)
    return response.payload.data.decode('UTF-8')

def format_payload_data(payload_data):
        formatted = {}
        
        if not payload_data:
            return formatted
        
        for item in payload_data:
            key = item.get('key')
            values = item.get('value', [{}])[0]  # Take the first element in the array
            
            # Getting the value that is not None
            value = (
                values.get('string_value') 
                or values.get('int_value') 
                or values.get('float_value') 
                or values.get('double_value')
            )
            
            formatted[key] = value
        
        return formatted