# GCP Libraries
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

# Utils
from utils.utils import BQ_CLIENT

# Aux libraries
from uuid import uuid4

class DatabaseLogger:
    """
    A utility class for logging messages to a BigQuery database.

    This class provides a method to insert log records into a specified BigQuery table, 
    storing details about event processing results.
    """

    @staticmethod
    def log_to_db(event_uuid: str, processing_result: str, processing_msg: str, processing_json: dict, dataset_delivernow, tbl_proc_log) -> str:
        """
        Logs a processing event to the database.

        This method inserts a record into a BigQuery table, storing details such as 
        the event UUID, processing result, and processing message.

        Args:
            event_uuid (str): Unique identifier of the event being logged.
            processing_result (str): The result of the processing (e.g., "SUCCESS", "FAILURE").
            processing_msg (str): A descriptive message regarding the processing outcome.

        Returns:
            str: The unique identifier (UUID) of the inserted log record.
        """
        print("Saving log...")
            
        record_uuid = str(uuid4())

        table =  f"{dataset_delivernow}.{tbl_proc_log}"

        query = f"""
            INSERT INTO `{table}` 
            (
                payload_record_uuid, 
                record_processing_uuid,
                record_processing_result, 
                record_processing_message, 
                record_processing_json
            )
            VALUES (
                @event_uuid,
                @record_uuid,
                @processing_result,
                @processing_msg,
                @processing_json
            );
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("event_uuid", "STRING", event_uuid),
                bigquery.ScalarQueryParameter("record_uuid", "STRING", record_uuid),
                bigquery.ScalarQueryParameter("processing_result", "STRING", processing_result),
                bigquery.ScalarQueryParameter("processing_msg", "STRING", processing_msg),
                bigquery.ScalarQueryParameter("processing_json", "JSON", processing_json)
            ]
        )

        try:
            query_job = BQ_CLIENT.query(query, job_config=job_config)
            query_job.result()
            print(f"Log saved in table {table}.")
        except GoogleAPIError as bq_error:
            error_msg = f"Error of BigQuery in the insertion of data: {bq_error}"
            print(error_msg) 
        except Exception as e:
            error_msg = f"Exception in the insertion of data: {e}"
            print(error_msg)
    
        return record_uuid