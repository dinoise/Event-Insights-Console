from typing import Dict, Any
from utils.utils import BQ_CLIENT, bigquery

class EventDataService:

    @staticmethod
    def get_table_columns(
        project_id: str, 
        dataset: str, 
        table: str,
        event_uuid: str
    ) -> Dict[str, Any]:
        if not table:
            raise ValueError("Table name can't be empty.")

        query = f"""
            SELECT * 
            FROM `{project_id}.{dataset}.{table}` 
            WHERE uuid_evento_origen = @event_uuid
            LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("event_uuid", "STRING", event_uuid)
            ]
        )

        query_job = BQ_CLIENT.query(query, job_config=job_config)
        results = query_job.result()
        
        for row in results:
            return {key: str(value) if value is not None else "" for key, value in row.items()}

        return {}
