"""
NSE Live Data Fetcher

Fetches real-time market data from NSE using nsepython library.
This module provides live data for:
- FII/DII flows
- India VIX  
- Market events
- Market status

Created: 2026-02-07
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import nsepython
try:
    from nsepython import (
        nse_fiidii,
        indiavix,
        nse_get_index_quote,
        nse_events,
        nse_marketStatus,
        nse_holidays,
        nse_most_active,
        is_market_open
    )
    NSEPYTHON_AVAILABLE = True
except ImportError:
    NSEPYTHON_AVAILABLE = False
    logger.warning("nsepython not installed. Live market data will use fallbacks.")


def get_live_fii_dii() -> Dict[str, Any]:
    """
    Get live FII/DII data from NSE.
    
    Returns:
        Dict with FII and DII net flows in crores
        
    Example:
        >>> data = get_live_fii_dii()
        >>> print(f"FII Net: {data['fii_net']} Cr")
    """
    if not NSEPYTHON_AVAILABLE:
        logger.warning("nsepython not available, returning placeholder FII/DII")
        return {
            "fii_net": 0,
            "dii_net": 0,
            "fii_buy": 0,
            "fii_sell": 0,
            "dii_buy": 0,
            "dii_sell": 0,
            "date": datetime.now().strftime("%d-%b-%Y"),
            "source": "placeholder"
        }
    
    try:
        df = nse_fiidii()
        
        fii_row = df[df['category'].str.contains('FII', case=False, na=False)]
        dii_row = df[df['category'] == 'DII']
        
        fii_net = float(fii_row['netValue'].values[0]) if len(fii_row) > 0 else 0
        dii_net = float(dii_row['netValue'].values[0]) if len(dii_row) > 0 else 0
        fii_buy = float(fii_row['buyValue'].values[0]) if len(fii_row) > 0 else 0
        fii_sell = float(fii_row['sellValue'].values[0]) if len(fii_row) > 0 else 0
        dii_buy = float(dii_row['buyValue'].values[0]) if len(dii_row) > 0 else 0
        dii_sell = float(dii_row['sellValue'].values[0]) if len(dii_row) > 0 else 0
        date_str = df['date'].values[0] if len(df) > 0 else datetime.now().strftime("%d-%b-%Y")
        
        # Determine flow signal
        net_flow = fii_net + dii_net
        if net_flow > 2000:
            flow_signal = "strong_inflow"
        elif net_flow > 500:
            flow_signal = "inflow"
        elif net_flow < -2000:
            flow_signal = "strong_outflow"
        elif net_flow < -500:
            flow_signal = "outflow"
        else:
            flow_signal = "neutral"
        
        return {
            "fii_net": fii_net,
            "dii_net": dii_net,
            "fii_buy": fii_buy,
            "fii_sell": fii_sell,
            "dii_buy": dii_buy,
            "dii_sell": dii_sell,
            "net_flow": net_flow,
            "flow_signal": flow_signal,
            "date": date_str,
            "source": "nsepython"
        }
        
    except Exception as e:
        logger.error(f"Error fetching FII/DII data: {e}")
        return {
            "fii_net": 0,
            "dii_net": 0,
            "error": str(e),
            "source": "error"
        }


def get_live_vix() -> Dict[str, Any]:
    """
    Get live India VIX from NSE.
    
    Returns:
        Dict with VIX value and interpretation
    """
    if not NSEPYTHON_AVAILABLE:
        return {"vix": 15.0, "regime": "normal", "source": "placeholder"}
    
    try:
        vix = indiavix()
        vix_value = float(vix) if vix else 15.0
        
        # Interpret VIX regime
        if vix_value < 12:
            regime = "low_fear"
            interpretation = "Extremely low volatility - complacency risk"
        elif vix_value < 15:
            regime = "calm"
            interpretation = "Low volatility - good for longs"
        elif vix_value < 20:
            regime = "normal"
            interpretation = "Normal volatility levels"
        elif vix_value < 25:
            regime = "elevated"
            interpretation = "Elevated fear - caution advised"
        elif vix_value < 30:
            regime = "high"
            interpretation = "High fear - reduce exposure"
        else:
            regime = "extreme"
            interpretation = "Extreme fear - potential capitulation"
        
        return {
            "vix": vix_value,
            "regime": regime,
            "interpretation": interpretation,
            "source": "nsepython"
        }
        
    except Exception as e:
        logger.error(f"Error fetching VIX: {e}")
        return {"vix": 15.0, "regime": "normal", "error": str(e), "source": "error"}


def get_live_index_quote(index_name: str = "NIFTY 50") -> Dict[str, Any]:
    """
    Get live index quote from NSE.
    
    Args:
        index_name: Index name (e.g., "NIFTY 50", "NIFTY BANK")
        
    Returns:
        Dict with index level and change
    """
    if not NSEPYTHON_AVAILABLE:
        return {"last": 0, "change": 0, "pct_change": 0, "source": "placeholder"}
    
    try:
        quote = nse_get_index_quote(index_name)
        
        # Parse the quote - handle string formatting
        last_str = quote.get('last', '0')
        last = float(str(last_str).replace(',', '')) if last_str else 0
        
        change = quote.get('change', 0) or 0
        pct_change = quote.get('percentChange', 0) or 0
        
        return {
            "index": index_name,
            "last": last,
            "change": change,
            "pct_change": pct_change,
            "source": "nsepython"
        }
        
    except Exception as e:
        logger.error(f"Error fetching index quote: {e}")
        return {"last": 0, "error": str(e), "source": "error"}


def get_upcoming_events(limit: int = 10) -> Dict[str, Any]:
    """
    Get upcoming NSE events (earnings, AGMs, etc.)
    
    Args:
        limit: Maximum events to return
        
    Returns:
        Dict with event list
    """
    if not NSEPYTHON_AVAILABLE:
        return {"events": [], "total": 0, "source": "placeholder"}
    
    try:
        events_df = nse_events()
        
        if events_df is None or len(events_df) == 0:
            return {"events": [], "total": 0, "source": "nsepython"}
        
        # Get relevant columns
        events_list = []
        for i, row in events_df.head(limit).iterrows():
            events_list.append({
                "symbol": row.get('symbol', ''),
                "company": row.get('company', ''),
                "purpose": row.get('purpose', ''),
                "date": row.get('date', '')
            })
        
        # Count by type
        event_types = events_df['purpose'].value_counts().head(5).to_dict() if 'purpose' in events_df.columns else {}
        
        return {
            "events": events_list,
            "total": len(events_df),
            "event_types": event_types,
            "source": "nsepython"
        }
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return {"events": [], "error": str(e), "source": "error"}


def get_market_status() -> Dict[str, Any]:
    """
    Get current market status.
    
    Returns:
        Dict with market open/close status
    """
    if not NSEPYTHON_AVAILABLE:
        return {"is_open": False, "status": "unknown", "source": "placeholder"}
    
    try:
        is_open = is_market_open()
        status_dict = nse_marketStatus()
        
        return {
            "is_open": is_open,
            "status_details": status_dict if isinstance(status_dict, dict) else {},
            "source": "nsepython"
        }
        
    except Exception as e:
        logger.error(f"Error fetching market status: {e}")
        return {"is_open": False, "error": str(e), "source": "error"}


def get_trading_holidays() -> Dict[str, Any]:
    """
    Get list of trading holidays.
    
    Returns:
        Dict with holiday list
    """
    if not NSEPYTHON_AVAILABLE:
        return {"holidays": [], "source": "placeholder"}
    
    try:
        holidays = nse_holidays('trading')
        
        return {
            "holidays": holidays if isinstance(holidays, list) else [],
            "count": len(holidays) if holidays else 0,
            "source": "nsepython"
        }
        
    except Exception as e:
        logger.error(f"Error fetching holidays: {e}")
        return {"holidays": [], "error": str(e), "source": "error"}


def get_live_market_data() -> Dict[str, Any]:
    """
    Get comprehensive live market data from NSE.
    
    Combines all live data sources:
    - FII/DII flows
    - India VIX
    - Index quote
    - Market status
    - Upcoming events
    
    Returns:
        Dict with all live market data
        
    Example:
        >>> data = get_live_market_data()
        >>> print(f"FII Net: {data['fii_dii']['fii_net']} Cr")
        >>> print(f"VIX: {data['vix']['vix']}")
    """
    return {
        "fii_dii": get_live_fii_dii(),
        "vix": get_live_vix(),
        "nifty_quote": get_live_index_quote("NIFTY 50"),
        "market_status": get_market_status(),
        "upcoming_events": get_upcoming_events(limit=10),
        "timestamp": datetime.now().isoformat(),
        "source": "nsepython" if NSEPYTHON_AVAILABLE else "placeholder"
    }


# Export all functions
__all__ = [
    "get_live_fii_dii",
    "get_live_vix",
    "get_live_index_quote",
    "get_upcoming_events",
    "get_market_status",
    "get_trading_holidays",
    "get_live_market_data",
    "NSEPYTHON_AVAILABLE"
]
