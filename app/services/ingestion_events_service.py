from utils.utils import BQ_CLIENT, bigquery, format_payload_data

from typing import List, Dict

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
    def get_event_by_uuid(project_id: str, dataset: str, tbl_ingestion_events: str, ingestion_event_id: str) -> Dict[str, any]:
        query = f"""
        SELECT 
            source_id,
            event_type_id,
            event_logical_name,
            event_type_topic_name,
            event_payload_format,
            ingestion_event_processing_stage,
            ingestion_event_source,
            event_created_by,
            event_payload_data
        FROM `{project_id}.{dataset}.{tbl_ingestion_events}`
        WHERE event_uuid = @event_uuid
        LIMIT 1;
        """

        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("event_uuid", "STRING", ingestion_event_id)
        ])

        try:
            query_job = BQ_CLIENT.query(query, job_config=job_config)
            result = query_job.result()
            row = next(result)
            
            # Formatear los datos
            formatted_data = {
                'source_id': row.source_id,
                'event_type_id': row.event_type_id,
                'event_logical_name': row.event_logical_name,
                'event_type_topic_name': row.event_type_topic_name,
                'event_payload_format': row.event_payload_format,
                'ingestion_event_processing_stage': row.ingestion_event_processing_stage,
                'ingestion_event_source': row.ingestion_event_source,
                'event_created_by': row.event_created_by,
                'event_payload_data': format_payload_data(row.event_payload_data)
            }            
        except StopIteration:
            print(f"No data for UUID: {ingestion_event_id}")
            return None
        except Exception as e:
            errro_msg = f"Error in the request: {e}"
            print(errro_msg)
            raise Exception(errro_msg)

        return formatted_data

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