"""
Data Quality Issues Analysis - IRCTC Macro Agent Example

CRITICAL FINDINGS from production data review:
"""

# Issue 1: Macro Agent Receiving Irrelevant Data
CURRENT_MACRO_AGENT_DATA = {
    "ticker": "IRCTC",
    "timestamp": "...",
    "sentiment": {...},  # ❌ NOT NEEDED - Macro doesn't analyze news
    "macro": {...},      # ✅ NEEDED
    "supabase_data": {...},  # ❌ Errors - not configured
    "quote": {...},      # ❌ NOT NEEDED - Daily price not relevant
    "fundamentals": {...},  # ⚠️ Only sector/industry needed
    "price_history": {  # ❌ NOT NEEDED - 251 days of OHLCV!
        "data": [251 records]  # Macro doesn't do technical analysis
    }
}

# Issue 2: Missing Critical Macro Data
MACRO_DATA_QUALITY = {
    "india_vix": {
        "error": "nsetools not installed",  # ❌ CRITICAL - VIX is key macro indicator
        "value": None  # ❌ Can't analyze fear/greed without this
    },
    "nifty_pe": None,  # ❌ CRITICAL - Can't assess market valuation
    "nifty_pb": None,  # ❌ CRITICAL - Can't assess market valuation
    "rbi_rates": {
        "source": "fallback_defaults",  # ⚠️ Using defaults, not live data
        "note": "Using default values. Install jugaad-data for live rates."
    }
}

# Issue 3: Supabase Errors Not Flagged
SUPABASE_ERRORS = {
    "scores": {"error": "Supabase not configured"},
    "weekly": {"error": "Supabase not configured"},
    "monthly": {"error": "Supabase not configured"},
    "seasonality": {"error": "Supabase not configured"}
}

# RECOMMENDED FIX:
CORRECTED_MACRO_AGENT_DATA = {
    "ticker": "IRCTC",
    "timestamp": "...",
    "current_price": 613.15,  # Just for context
    "company_name": "Indian Railway Catering & Tourism Corporation Limited",
    
    # Only sector/industry from fundamentals
    "sector": "Consumer Cyclical",
    "industry": "Travel Services",
    "pe_ratio": 35.79,  # For valuation overlay
    "market_cap": 490520018944,  # For size context
    
    # Full macro data (this is what macro agent needs)
    "macro": {
        "rbi_rates": {...},
        "india_vix": {...},  # MUST have valid value
        "nifty_valuations": {...},  # MUST have PE/PB
        "market_regime": "cautious"
    },
    
    # NO price_history
    # NO sentiment
    # NO quote details
    # NO supabase_data (if errors)
}

# VALIDATION RULES NEEDED:
VALIDATION_CHECKS = {
    "macro_agent": {
        "required_fields": [
            "macro.india_vix.value",  # Must not be None
            "macro.nifty_pe",  # Must not be None
            "macro.rbi_rates.repo_rate",
            "sector",  # For sector-specific macro impacts
        ],
        "forbidden_fields": [
            "price_history",  # Macro doesn't analyze charts
            "sentiment.headlines",  # Macro doesn't analyze news
        ],
        "max_data_size": 5000  # chars (currently sending 50,000+)
    }
}

print("=" * 80)
print("CRITICAL DATA QUALITY ISSUES IDENTIFIED")
print("=" * 80)
print("\n1. Macro agent receiving 251 days of price history (NOT NEEDED)")
print("2. india_vix.value is NULL (CRITICAL - can't analyze market)")
print("3. nifty_pe/pb are NULL (CRITICAL - can't assess valuation)")
print("4. Supabase errors not flagged during testing")
print("5. No validation for missing/null critical fields")
print("\n" + "=" * 80)
