#!/usr/bin/env python3
"""
Generate comprehensive database schema documentation for TransfusionIQ
"""

import sys
import json
from sqlalchemy import create_engine, MetaData, inspect
from app.core.config import settings

def generate_human_readable_docs():
    """Generate human-readable schema documentation"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    print('=' * 80)
    print('TRANFUSIONIQ - COMPLETE DATABASE SCHEMA DOCUMENTATION')
    print('=' * 80)
    print()

    # Get all tables
    tables = inspector.get_table_names()
    print(f'📊 TOTAL TABLES: {len(tables)}')
    print()

    # Document each table
    for table_name in sorted(tables):
        print('─' * 80)
        print(f'📋 TABLE: {table_name}')
        print('─' * 40)
        
        # Get columns
        columns = inspector.get_columns(table_name)
        print('COLUMNS:')
        for col in columns:
            nullable = 'NULL' if col['nullable'] else 'NOT NULL'
            default = f"DEFAULT: {col['default']}" if col['default'] else ''
            print(f'  • {col["name"]:25} {str(col["type"]):30} {nullable:10} {default}')
        
        # Get primary keys
        pk = inspector.get_pk_constraint(table_name)
        if pk['constrained_columns']:
            print(f'\nPRIMARY KEY: {pk["constrained_columns"]}')
        
        # Get foreign keys
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print('\nFOREIGN KEYS:')
            for fk in fks:
                print(f'  • {fk["constrained_columns"]} → {fk["referred_table"]}({fk["referred_columns"]})')
        
        # Get indexes
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print('\nINDEXES:')
            for idx in indexes:
                unique = 'UNIQUE ' if idx['unique'] else ''
                print(f'  • {unique}{idx["name"]}: {idx["column_names"]}')
        
        print()

def generate_json_schema():
    """Generate JSON schema for AI consumption"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)

    schema_data = {
        'project': 'TransfusionIQ - Blood Transfusion CDS System',
        'description': 'Clinical Decision Support System with Analytics and Hospital Management',
        'database': 'PostgreSQL',
        'tables': {}
    }

    tables = inspector.get_table_names()
    for table_name in sorted(tables):
        table_info = {
            'columns': [],
            'primary_key': None,
            'foreign_keys': [],
            'indexes': []
        }
        
        # Columns
        for col in inspector.get_columns(table_name):
            table_info['columns'].append({
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable'],
                'default': str(col['default']) if col['default'] else None
            })
        
        # Primary key
        pk = inspector.get_pk_constraint(table_name)
        if pk['constrained_columns']:
            table_info['primary_key'] = pk['constrained_columns']
        
        # Foreign keys
        for fk in inspector.get_foreign_keys(table_name):
            table_info['foreign_keys'].append({
                'columns': fk['constrained_columns'],
                'references': f'{fk["referred_table"]}({fk["referred_columns"]})'
            })
        
        # Indexes
        for idx in inspector.get_indexes(table_name):
            table_info['indexes'].append({
                'name': idx['name'],
                'columns': idx['column_names'],
                'unique': idx['unique']
            })
        
        schema_data['tables'][table_name] = table_info

    # Save to file
    with open('database_schema.json', 'w') as f:
        json.dump(schema_data, f, indent=2, default=str)
    
    print('\n✅ Generated database_schema.json file')
    print('📁 Location: C:\\Users\\mdmho\\transfusion-cds\\backend\\database_schema.json')

def generate_er_diagram():
    """Generate Entity-Relationship diagram"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print('\n' + '=' * 80)
    print('ENTITY-RELATIONSHIP DIAGRAM')
    print('=' * 80)
    print()

    # Group by functional areas
    core_tables = ['users', 'hospitals', 'hospital_configs']
    patient_tables = ['patient_encounters']
    clinical_tables = ['recommendations', 'audit_logs']
    analytics_tables = ['blood_product_cost', 'analytics_monthly_summary']

    print('🏥 CORE TABLES (Authentication & Hospital Management):')
    for table in core_tables:
        if table in tables:
            print(f'  • {table}')
    print()

    print('👤 PATIENT DATA:')
    for table in patient_tables:
        if table in tables:
            print(f'  • {table}')
    print()

    print('⚕️ CLINICAL DECISION SUPPORT:')
    for table in clinical_tables:
        if table in tables:
            print(f'  • {table}')
    print()

    print('📊 ANALYTICS & ROI TRACKING:')
    for table in analytics_tables:
        if table in tables:
            print(f'  • {table}')
    print()

    print('🔗 KEY RELATIONSHIPS:')
    relationships = [
        'users → hospitals (hospital_id)',
        'patient_encounters → hospitals (hospital_id)',
        'patient_encounters → users (created_by)',
        'recommendations → patient_encounters (encounter_id)',
        'audit_logs → recommendations (recommendation_id)',
        'audit_logs → users (user_id)',
        'blood_product_cost → hospitals (hospital_id)',
        'analytics_monthly_summary → hospitals (hospital_id)',
        'hospital_configs → hospitals (hospital_id)'
    ]
    
    for rel in relationships:
        print(f'   {rel}')

def main():
    """Main function"""
    print("🔍 Generating TransfusionIQ Database Documentation...")
    print()
    
    # Generate all documentation
    generate_human_readable_docs()
    generate_json_schema()
    generate_er_diagram()
    
    print('\n' + '=' * 80)
    print('✅ DATABASE DOCUMENTATION COMPLETE')
    print('=' * 80)
    print('\nFiles generated:')
    print('1. Console output (human readable)')
    print('2. database_schema.json (AI readable)')
    print('\nUse this documentation to help AI understand your database structure instantly.')

if __name__ == '__main__':
    main()