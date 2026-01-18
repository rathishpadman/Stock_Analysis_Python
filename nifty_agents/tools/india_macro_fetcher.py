"""
India Macro Economic Data Fetcher

Fetches macro-economic indicators for Indian market analysis:
- RBI policy rates (Repo, CRR, SLR)
- India VIX (volatility/fear index)
- NIFTY valuations (PE, PB)
- Market regime determination

Data Sources:
- jugaad-data: RBI rates (if available)
- nsetools: India VIX, NIFTY PE/PB
- Fallback calculations for unavailable data
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Try to import optional dependencies
try:
    from nsetools import Nse
    NSETOOLS_AVAILABLE = True
except ImportError:
    NSETOOLS_AVAILABLE = False

try:
    from jugaad_data.rbi import RBI
    JUGAAD_RBI_AVAILABLE = True
except ImportError:
    JUGAAD_RBI_AVAILABLE = False

logger = logging.getLogger(__name__)


# Default/fallback RBI rates (update periodically)
DEFAULT_RBI_RATES = {
    "repo_rate": 6.50,
    "reverse_repo_rate": 3.35,
    "bank_rate": 6.75,
    "crr": 4.50,
    "slr": 18.00,
    "msf_rate": 6.75,
    "source": "fallback_defaults",
    "note": "Using default values. Install jugaad-data for live rates."
}


def get_rbi_rates() -> Dict[str, Any]:
    """
    Get current RBI monetary policy rates.
    
    Fetches:
    - Repo Rate: Rate at which RBI lends to banks
    - Reverse Repo Rate: Rate at which RBI borrows from banks
    - CRR: Cash Reserve Ratio
    - SLR: Statutory Liquidity Ratio
    - Bank Rate: Long-term lending rate
    - MSF Rate: Marginal Standing Facility rate
    
    Also determines policy stance (hawkish/dovish/neutral) based on rates.
    
    Returns:
        Dict with RBI rates and policy interpretation
        
    Example:
        >>> rates = get_rbi_rates()
        >>> print(f"Repo Rate: {rates['repo_rate']}%")
        >>> print(f"Policy Stance: {rates['policy_stance']}")
    """
    rates = {}
    
    if JUGAAD_RBI_AVAILABLE:
        try:
            rbi = RBI()
            current_rates = rbi.current_rates()
            
            rates = {
                "repo_rate": current_rates.get("repo_rate"),
                "reverse_repo_rate": current_rates.get("reverse_repo_rate"),
                "bank_rate": current_rates.get("bank_rate"),
                "crr": current_rates.get("crr"),
                "slr": current_rates.get("slr"),
                "msf_rate": current_rates.get("msf_rate"),
                "source": "jugaad_data_rbi",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Failed to fetch RBI rates from jugaad-data: {e}")
            rates = DEFAULT_RBI_RATES.copy()
    else:
        rates = DEFAULT_RBI_RATES.copy()
    
    # Determine policy stance based on repo rate
    repo_rate = rates.get("repo_rate", 6.0)
    if repo_rate >= 7.0:
        rates["policy_stance"] = "hawkish"
        rates["stance_description"] = "Tight monetary policy - higher rates to control inflation"
    elif repo_rate <= 5.0:
        rates["policy_stance"] = "dovish"
        rates["stance_description"] = "Accommodative policy - lower rates to boost growth"
    else:
        rates["policy_stance"] = "neutral"
        rates["stance_description"] = "Balanced approach between growth and inflation control"
    
    rates["timestamp"] = datetime.now().isoformat()
    return rates


def get_india_vix() -> Dict[str, Any]:
    """
    Get India VIX (Volatility Index) - the fear gauge of Indian markets.
    
    VIX Interpretation:
    - < 15: Low fear/complacency (bullish sentiment)
    - 15-20: Normal/moderate volatility
    - 20-25: Elevated concern
    - 25-30: High fear
    - > 30: Extreme fear/panic
    
    Returns:
        Dict with VIX value and fear level interpretation
        
    Example:
        >>> vix = get_india_vix()
        >>> print(f"India VIX: {vix['value']} ({vix['fear_level']})")
    """
    if not NSETOOLS_AVAILABLE:
        return {
            "error": "nsetools not installed",
            "value": None,
            "fear_level": "unknown",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        nse = Nse()
        vix_data = nse.get_index_quote("INDIA VIX")
        
        if not vix_data:
            return {
                "error": "Could not fetch India VIX",
                "value": None,
                "fear_level": "unknown",
                "timestamp": datetime.now().isoformat()
            }
        
        vix_value = vix_data.get("last", 0)
        change_pct = vix_data.get("percentChange", 0)
        
        # Determine fear level
        if vix_value < 15:
            fear_level = "low"
            description = "Low volatility - Market complacency, bullish sentiment"
        elif vix_value < 20:
            fear_level = "moderate"
            description = "Normal volatility - Balanced market sentiment"
        elif vix_value < 25:
            fear_level = "elevated"
            description = "Elevated volatility - Growing concern in markets"
        elif vix_value < 30:
            fear_level = "high"
            description = "High volatility - Significant fear in markets"
        else:
            fear_level = "extreme"
            description = "Extreme volatility - Panic/crisis mode"
        
        return {
            "index": "INDIA VIX",
            "value": vix_value,
            "change": vix_data.get("variation"),
            "change_pct": change_pct,
            "fear_level": fear_level,
            "description": description,
            "data_source": "nsetools",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching India VIX: {e}")
        return {
            "error": f"Error fetching India VIX: {str(e)}",
            "value": None,
            "fear_level": "unknown",
            "timestamp": datetime.now().isoformat()
        }


def get_nifty_valuations() -> Dict[str, Any]:
    """
    Get NIFTY 50 valuation metrics (PE, PB, Dividend Yield).
    
    Valuation Interpretation:
    - PE < 18: Undervalued
    - PE 18-22: Fair value
    - PE 22-25: Slightly overvalued
    - PE > 25: Overvalued
    
    Returns:
        Dict with NIFTY valuations and interpretation
    """
    if not NSETOOLS_AVAILABLE:
        return {
            "error": "nsetools not installed",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        nse = Nse()
        nifty_data = nse.get_index_quote("NIFTY 50")
        
        if not nifty_data:
            return {"error": "Could not fetch NIFTY data"}
        
        pe = nifty_data.get("pe", 0)
        pb = nifty_data.get("pb", 0)
        dy = nifty_data.get("dy", 0)
        
        # PE interpretation
        if pe < 18:
            pe_interpretation = "undervalued"
        elif pe < 22:
            pe_interpretation = "fair_value"
        elif pe < 25:
            pe_interpretation = "slightly_overvalued"
        else:
            pe_interpretation = "overvalued"
        
        return {
            "index": "NIFTY 50",
            "pe": pe,
            "pb": pb,
            "dividend_yield": dy,
            "pe_interpretation": pe_interpretation,
            "value": nifty_data.get("last"),
            "data_source": "nsetools",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching NIFTY valuations: {e}")
        return {
            "error": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def determine_market_regime(indicators: Dict[str, Any]) -> str:
    """
    Determine overall market regime based on multiple indicators.
    
    Factors considered:
    - India VIX level (fear/greed)
    - NIFTY PE (valuation)
    - RBI policy stance
    
    Args:
        indicators: Dict containing india_vix, nifty_pe, rbi_rates
    
    Returns:
        Market regime: 'bullish', 'bearish', 'neutral', 'cautious'
        
    Example:
        >>> regime = determine_market_regime({
        ...     "india_vix": {"value": 12.0},
        ...     "nifty_pe": 20.0,
        ...     "rbi_rates": {"repo_rate": 6.0}
        ... })
        >>> print(regime)
        'bullish'
    """
    score = 0  # Positive = bullish, Negative = bearish
    
    # VIX contribution (-2 to +2)
    vix_data = indicators.get("india_vix", {})
    vix_value = vix_data.get("value", 20)
    if vix_value:
        if vix_value < 15:
            score += 2  # Low fear = bullish
        elif vix_value < 20:
            score += 1
        elif vix_value < 25:
            score -= 1
        else:
            score -= 2  # High fear = bearish
    
    # NIFTY PE contribution (-2 to +2)
    nifty_pe = indicators.get("nifty_pe")
    if nifty_pe:
        if nifty_pe < 18:
            score += 2  # Undervalued = bullish
        elif nifty_pe < 22:
            score += 1
        elif nifty_pe < 25:
            score -= 1
        else:
            score -= 2  # Overvalued = bearish
    
    # RBI rates contribution (-1 to +1)
    rbi_data = indicators.get("rbi_rates", {})
    repo_rate = rbi_data.get("repo_rate", 6.0)
    if repo_rate:
        if repo_rate < 5.5:
            score += 1  # Dovish = bullish for equities
        elif repo_rate > 7.0:
            score -= 1  # Hawkish = bearish for equities
    
    # Determine regime based on score
    if score >= 3:
        return "bullish"
    elif score >= 1:
        return "neutral"
    elif score >= -2:
        return "cautious"
    else:
        return "bearish"


def get_macro_indicators() -> Dict[str, Any]:
    """
    Get all macro-economic indicators in a single call.
    
    Fetches:
    - RBI policy rates
    - India VIX
    - NIFTY valuations
    - Market regime determination
    
    Returns:
        Comprehensive macro indicators dict
        
    Example:
        >>> macro = get_macro_indicators()
        >>> print(f"Market Regime: {macro['market_regime']}")
        >>> print(f"India VIX: {macro['india_vix']['value']}")
    """
    result = {
        "timestamp": datetime.now().isoformat()
    }
    
    # Fetch RBI rates
    try:
        result["rbi_rates"] = get_rbi_rates()
    except Exception as e:
        logger.error(f"Failed to fetch RBI rates: {e}")
        result["rbi_rates"] = {"error": str(e)}
    
    # Fetch India VIX
    try:
        result["india_vix"] = get_india_vix()
    except Exception as e:
        logger.error(f"Failed to fetch India VIX: {e}")
        result["india_vix"] = {"error": str(e)}
    
    # Fetch NIFTY valuations
    try:
        nifty_vals = get_nifty_valuations()
        result["nifty_valuations"] = nifty_vals
        result["nifty_pe"] = nifty_vals.get("pe")
        result["nifty_pb"] = nifty_vals.get("pb")
    except Exception as e:
        logger.error(f"Failed to fetch NIFTY valuations: {e}")
        result["nifty_valuations"] = {"error": str(e)}
    
    # Determine market regime
    try:
        result["market_regime"] = determine_market_regime(result)
    except Exception as e:
        logger.error(f"Failed to determine market regime: {e}")
        result["market_regime"] = "unknown"
    
    return result


def get_market_breadth() -> Dict[str, Any]:
    """
    Get market breadth indicators (advances/declines).
    
    Returns:
        Dict with advances, declines, and breadth ratio
    """
    if not NSETOOLS_AVAILABLE:
        return {"error": "nsetools not installed"}
    
    try:
        nse = Nse()
        nifty_data = nse.get_index_quote("NIFTY 50")
        
        advances = nifty_data.get("advances", 0)
        declines = nifty_data.get("declines", 0)
        unchanged = nifty_data.get("unchanged", 0)
        
        # Calculate breadth ratio
        total = advances + declines
        breadth_ratio = (advances / total) if total > 0 else 0.5
        
        # Interpret breadth
        if breadth_ratio > 0.7:
            breadth_signal = "strong_bullish"
        elif breadth_ratio > 0.55:
            breadth_signal = "bullish"
        elif breadth_ratio > 0.45:
            breadth_signal = "neutral"
        elif breadth_ratio > 0.3:
            breadth_signal = "bearish"
        else:
            breadth_signal = "strong_bearish"
        
        return {
            "advances": advances,
            "declines": declines,
            "unchanged": unchanged,
            "breadth_ratio": round(breadth_ratio, 2),
            "breadth_signal": breadth_signal,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching market breadth: {e}")
        return {"error": str(e)}
