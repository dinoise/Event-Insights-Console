from typing import Dict, Any
from utils.utils import BQ_CLIENT, bigquery

class EventDataService:

    @staticmethod
    def get_table_columns(
        project_id: str, 
        dataset: str, 
        table: str,
        id_cliente: str
    ) -> Dict[str, Any]:
        if not table:
            raise ValueError("Table name can't be empty.")

        query = f"""
            SELECT * 
            FROM `{project_id}.{dataset}.{table}` 
            WHERE id_cliente = @id_cliente
            LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id_cliente", "STRING", id_cliente)
            ]
        )

        query_job = BQ_CLIENT.query(query, job_config=job_config)
        results = query_job.result()
        
        for row in results:
            return {key: str(value) if value is not None else "" for key, value in row.items()}

        return {}
