import os
from supabase import create_client
import sys
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()
    
    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found in environment.")
        sys.exit(1)
        
    print(f"Testing connection to: {url[:15]}...")
    
    try:
        supabase = create_client(url, key)
        # Verify specific ticker
        ticker = "NATIONALUM"
        res = supabase.table("daily_stocks").select("*").eq("ticker", ticker).order("date", desc=True).limit(1).execute()
        
        if res.data:
            row = res.data[0]
            print(f"✅ Found data for {row.get('ticker')}")
            
            # Identify and print null fields
            null_fields = [k for k, v in row.items() if v is None or v == '']
            print(f"\nTotal Fields: {len(row)}")
            print(f"Null/Empty Fields ({len(null_fields)}):")
            for f in sorted(null_fields):
                print(f"- {f}")
        else:
            print(f"No data found for {ticker}")
            
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
