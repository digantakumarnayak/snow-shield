import argparse
import os
import pandas as pd
import snowflake.connector

def connect_snowflake():
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )

def map_type(dtype):
    if 'int' in str(dtype): return 'NUMBER'
    elif 'float' in str(dtype): return 'FLOAT'
    elif 'bool' in str(dtype): return 'BOOLEAN'
    else: return 'VARCHAR(16777216)'

def ingest_secure_csv(file_path, table_name):
    print(f"🔍 [Risk & Compliance Scan] Analyzing local file: {file_path}...")
    
    # Load data
    df = pd.read_csv(file_path)
    
    # Compliance Rule: Automatically mask sensitive PII fields before cloud upload
    for col in df.columns:
        if 'email' in col.lower():
            print(f"🔒 Masking sensitive email column: {col}")
            df[col] = df[col].apply(lambda x: str(x)[0] + "***@" + str(x).split('@')[-1] if '@' in str(x) else "MASKED")
        elif 'card' in col.lower() or 'cc' in col.lower():
            print(f"🔒 Masking sensitive credit card column: {col}")
            df[col] = df[col].apply(lambda x: "****-****-****-" + str(x)[-4:] if len(str(x)) >= 4 else "MASKED")

    # Save sanitized file locally
    sanitized_path = "sanitized_upload.csv"
    df.to_csv(sanitized_path, index=False)
    
    columns_spec = ", ".join([f'"{col.upper()}" {map_type(dtype)}' for col, dtype in df.dtypes.items()])
    ctx = connect_snowflake()
    cs = ctx.cursor()
    
    try:
        print(f"🏗️ Creating target compliance table '{table_name.upper()}'...")
        cs.execute(f'CREATE TABLE IF NOT EXISTS "{table_name.upper()}" ({columns_spec})')
        
        stage_name = f"temp_compliance_stage"
        cs.execute(f'CREATE OR REPLACE TEMPORARY STAGE {stage_name}')
        
        abs_path = os.path.abspath(sanitized_path).replace("\\", "/")
        print(f"📤 Uploading anonymized data securely to Snowflake stage...")
        cs.execute(f"PUT 'file://{abs_path}' @{stage_name} AUTO_COMPRESS=TRUE")
        
        print(f"🚀 Executing regulated streaming pipeline...")
        cs.execute(f"""
            COPY INTO "{table_name.upper()}" 
            FROM @{stage_name} 
            FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"')
            PURGE = TRUE
        """)
        print("✅ Success! Anonymized audit logs securely ingested into Snowflake.")
        
    except Exception as e:
        print(f"❌ Regulatory pipeline error: {e}")
    finally:
        cs.close()
        ctx.close()
        if os.path.exists(sanitized_path):
            os.remove(sanitized_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="snow-shield: Regulated Data Intelligence & Ingestion CLI for Snowflake.")
    subparsers = parser.add_subparsers(dest="command")
    ingest_parser = subparsers.add_parser("ingest", help="Sanitize PII and upload file to Snowflake.")
    ingest_parser.add_argument("--file", required=True, help="Path to local transaction/audit log CSV.")
    ingest_parser.add_argument("--table", required=True, help="Target compliance table.")
    
    args = parser.parse_args()
    if args.command == "ingest":
        ingest_secure_csv(args.file, args.table)
