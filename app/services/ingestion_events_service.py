from utils.utils import BQ_CLIENT

from typing import List, Dict, Any

class IngestionEventService:

    @staticmethod
    def get_all_ingestion_events(
        project_id: str, 
        dataset: str, 
        tbl_clientes: str, 
        tbl_envios: str, 
        tbl_pedidos: str, 
        page: int = 1, 
        per_page: int = 50
    ) -> List[Dict[str, str]]:
        offset = (page - 1) * per_page
        
        query = f"""
        WITH combined_events AS (
            SELECT 
                uuid_evento_origen,
                evento_origen_mensaje,
                timestamp_creacion,
                '{tbl_clientes}' AS source_table
            FROM 
                `{project_id}.{dataset}.{tbl_clientes}`
            WHERE 
                uuid_evento_origen IS NOT NULL

            UNION ALL

            SELECT 
                uuid_evento_origen,
                evento_origen_mensaje,
                timestamp_creacion,
                '{tbl_envios}' AS source_table
            FROM 
                `{project_id}.{dataset}.{tbl_envios}`
            WHERE 
                uuid_evento_origen IS NOT NULL

            UNION ALL

            SELECT 
                uuid_evento_origen,
                evento_origen_mensaje,
                timestamp_creacion,
                '{tbl_pedidos}' AS source_table
            FROM 
                `{project_id}.{dataset}.{tbl_pedidos}`
            WHERE 
                uuid_evento_origen IS NOT NULL
        )
        SELECT 
            uuid_evento_origen,
            evento_origen_mensaje,
            timestamp_creacion,
            source_table
        FROM 
            combined_events
        ORDER BY 
            timestamp_creacion DESC
        LIMIT {per_page}
        OFFSET {offset}
        """
        
        query_job = BQ_CLIENT.query(query)
        result = query_job.result()
        
        return [dict(row) for row in result]

    @staticmethod
    def get_total_count(project_id: str, dataset: str, tbl_clientes: str, tbl_envios: str, tbl_pedidos: str) -> int:
        query = f"""
        SELECT COUNT(*) as total FROM (
            SELECT uuid_evento_origen FROM `{project_id}.{dataset}.{tbl_clientes}` WHERE uuid_evento_origen IS NOT NULL
            UNION ALL
            SELECT uuid_evento_origen FROM `{project_id}.{dataset}.{tbl_envios}` WHERE uuid_evento_origen IS NOT NULL
            UNION ALL
            SELECT uuid_evento_origen FROM `{project_id}.{dataset}.{tbl_pedidos}` WHERE uuid_evento_origen IS NOT NULL
        )
        """
        query_job = BQ_CLIENT.query(query)
        result = query_job.result()
        return next(result).total