# Models
from models.event_mapping import EventMapping

# Schemas
from schemas.event_mapping_schema import EventMappingSchema

# Types
from typing import List, Dict, Any

# Bigquery client
from utils.utils import BQ_CLIENT, bigquery

from __init__ import db

class EventMappingService:

    @staticmethod
    def get_all_event_mappings() -> List[Dict[str, Any]]:
        mappings = EventMapping.query.filter_by(
            event_mapping_status='ACTIVE'
        ).all()

        if not mappings: 
            return None
        
        return EventMappingSchema(many=True).dump(mappings)
    
    @staticmethod
    def get_event_mapping_by_pk(mapping_id: int) -> Dict[str, str]:
        mapping = EventMapping.query.filter_by(
            event_mapping_id=mapping_id,
            event_mapping_status='ACTIVE'
        ).first()
        
        return EventMappingSchema(many=False).dump(mapping)
    
    @staticmethod
    def get_all_event_mappings_by_event_type_id(event_type_id: int) -> List[Dict[str, str]]:
        mapping = EventMapping.query.filter_by(
            event_type_id=event_type_id,
            event_mapping_status='ACTIVE'
        ).all()
        
        return EventMappingSchema(many=True).dump(mapping)
    
    @staticmethod
    def get_all_event_mappings_by_source_id(source_id: int) -> List[Dict[str, str]]:
        mapping = EventMapping.query.filter_by(
            source_id=source_id,
            event_mapping_status='ACTIVE'
        ).all()
        
        return EventMappingSchema(many=True).dump(mapping)
    
    @staticmethod
    def validate_existence_bq(project_id: str, dataset: str, table: str = None) -> bool:
        if table:
            query = f"""
                SELECT COUNT(*) AS count
                FROM `{project_id}.{dataset}`.INFORMATION_SCHEMA.TABLES
                WHERE table_name = @table
            """
            query_params = [bigquery.ScalarQueryParameter("table", "STRING", table)]
        else:
            query = f"""
                SELECT COUNT(*) AS count
                FROM `{project_id}`.INFORMATION_SCHEMA.SCHEMATA
                WHERE SCHEMA_NAME = @dataset
            """
            query_params = [bigquery.ScalarQueryParameter("dataset", "STRING", dataset)]

        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        query_job = BQ_CLIENT.query(query, job_config=job_config)
        result = query_job.result()
        row = list(result)[0]

        return row["count"] > 0

    @staticmethod
    def get_table_columns(project_id: str, dataset: str, table: str) -> List[Dict[str, str]]:
        if not table:
            raise ValueError("Table name can't be empty.")

        EXCLUDED_FIELDS = {
            "timestamp_creacion",
            "creado_por",
            "uuid_evento_origen",
            "evento_origen_mensaje"
        }

        query = f"""
            SELECT
                ordinal_position AS sequence,
                column_name AS target_column,
                CASE 
                    WHEN is_nullable = 'YES' THEN 1 
                    ELSE 0 
                END AS nullable,
                data_type
            FROM
                `{project_id}.{dataset}.INFORMATION_SCHEMA.COLUMNS`
            WHERE 
                table_name = @table
            ORDER BY 
                ordinal_position;
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("table", "STRING", table)
            ]
        )

        try:
            query_job = BQ_CLIENT.query(query, job_config=job_config)
            results = query_job.result()
            
            return [
                dict(row.items())
                for row in results
                if not any(value in EXCLUDED_FIELDS for value in row.values())
            ]
        except Exception as e:
            print(f"Error getting the columns: {e}")
            return []
    
    @staticmethod
    def create_mapping(
        event_type_id: int, 
        source_id: int, 
        event_mapping_description: str, 
        event_mapping_version: float, 
        event_mapping_target_dataset: str, 
        event_mapping_target_table: str
    ) -> int:
        new_mapping = EventMapping(
            event_type_id=event_type_id,
            source_id=source_id,
            event_mapping_description=event_mapping_description,
            event_mapping_version=event_mapping_version,
            event_mapping_target_dataset=event_mapping_target_dataset,
            event_mapping_target_table=event_mapping_target_table,
            event_mapping_status="ACTIVE",
            event_mapping_created_by="system"
        )
        db.session.add(new_mapping)
        db.session.commit()

        return new_mapping.event_mapping_id  
    
    @staticmethod
    def update_mapping(mapping_id: int, update_data: Dict) -> List[Dict[str, Any]]:
        try:
            column = EventMapping.query.get(mapping_id)
            if not column:
                return None

            for field, value in update_data.items():
                setattr(column, field, value)
            
            db.session.commit()

            return EventMappingSchema(many=False).dump(column)
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
        
    @staticmethod
    def delete_mapping(mapping_id: int) -> List[Dict[str, Any]]:
        try:
            column = EventMapping.query.get(mapping_id)
            if not column:
                return None

            setattr(column, "event_mapping_status", "INACTIVE")
            
            db.session.commit()

            return EventMappingSchema(many=False).dump(column)
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
        