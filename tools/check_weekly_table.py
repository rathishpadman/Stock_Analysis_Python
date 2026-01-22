
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def check_table():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    client = create_client(url, key)
    
    print("Checking for 'weekly_analysis' table...")
    try:
        # Try to select 1 row
        res = client.table("weekly_analysis").select("*").limit(1).execute()
        print("Table exists.")
        if res.data:
            print(f"Sample data: {res.data[0]}")
        else:
            print("Table is empty.")
    except Exception as e:
        print(f"Error (Table likely missing): {e}")

if __name__ == "__main__":
    check_table()
