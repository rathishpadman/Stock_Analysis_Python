
import os
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def check_dates():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    client = create_client(url, key)
    
    print("Fetching date distribution...")
    try:
        # Fetch just dates
        res = client.table("daily_stocks").select("date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            print(df['date'].value_counts().sort_index())
        else:
            print("No data found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_dates()
