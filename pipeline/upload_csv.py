
import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import math

load_dotenv()

def upload_csv():
    # Configuration
    csv_path = "data/nifty200_staging.csv"
    table_name = "daily_stocks"
    batch_size = 50
    
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    # Connect to Supabase
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("Missing Supabase credentials in .env")
        return
        
    client = create_client(url, key)
    
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Replace NaN with None (NULL in SQL)
    df = df.where(pd.notnull(df), None)
    
    records = df.to_dict(orient="records")
    total = len(records)
    print(f"Uploading {total} records to '{table_name}'...")
    
    # Upload in batches
    success_count = 0
    for i in range(0, total, batch_size):
        batch = records[i:i+batch_size]
        try:
            client.table(table_name).upsert(batch).execute()
            print(f"  Uploaded {i + len(batch)}/{total}...")
            success_count += len(batch)
        except Exception as e:
            print(f"  Error in batch {i}: {e}")
            
    print(f"Upload complete. {success_count}/{total} successful.")

if __name__ == "__main__":
    upload_csv()
