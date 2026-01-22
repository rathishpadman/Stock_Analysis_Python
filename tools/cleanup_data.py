
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def cleanup():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    client = create_client(url, key)
    
    target_date = "2026-01-14"
    print(f"Deleting records before {target_date}...")
    
    try:
        # Delete where date < target_date
        res = client.table("daily_stocks").delete().lt("date", target_date).execute()
        print(f"Cleanup complete. Deleted records: {len(res.data) if res.data else 'Unknown'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    cleanup()
