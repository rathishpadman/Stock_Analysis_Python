"""
Comprehensive Agent Data Audit - Real Data Analysis

This script:
1. Fetches REAL production data for a stock
2. Shows what each agent CURRENTLY receives
3. Identifies IRRELEVANT data per agent
4. Identifies MISSING/NULL critical fields
5. Validates data relevance based on agent prompts
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator

# Agent data requirements based on prompt analysis
AGENT_REQUIREMENTS = {
    "fundamental_agent": {
        "description": "Analyzes P/E, P/B, ROE, ROCE, Debt/Equity, business models, governance",
        "required_data": [
            "fundamentals.pe_ratio",
            "fundamentals.pb_ratio",
            "fundamentals.roe",
            "fundamentals.debt_to_equity",
            "fundamentals.sector",
            "current_price"
        ],
        "optional_data": [
            "fundamentals.market_cap",
            "fundamentals.profit_margin",
            "supabase_data.scores"
        ],
        "irrelevant_data": [
            "price_history",  # Doesn't analyze charts
            "macro",  # Not a macro analyst
            "sentiment.headlines"  # Doesn't analyze news
        ]
    },
    "technical_agent": {
        "description": "Analyzes charts, patterns, S/R, RSI, MACD, volume, moving averages",
        "required_data": [
            "price_history.data",  # Needs price data for patterns
            "current_price",
            "quote.volume"
        ],
        "optional_data": [
            "supabase_data.scores.rsi14",
            "supabase_data.scores.macd_signal",
            "macro.market_regime"  # For Nifty direction context
        ],
        "irrelevant_data": [
            "fundamentals.pe_ratio",  # Doesn't analyze financials
            "fundamentals.roe",
            "sentiment.headlines",  # Doesn't analyze news
            "macro.rbi_rates"  # Doesn't analyze macro
        ]
    },
    "sentiment_agent": {
        "description": "Analyzes news sentiment, headlines, VIX for fear/greed, upcoming events",
        "required_data": [
            "sentiment.overall_sentiment",
            "sentiment.headlines",
            "macro.india_vix"  # For fear/greed
        ],
        "optional_data": [
            "sentiment.sentiment_score",
            "macro.market_regime",
            "fundamentals.sector"  # For news filtering
        ],
        "irrelevant_data": [
            "price_history",  # Doesn't analyze charts
            "fundamentals.pe_ratio",  # Doesn't analyze financials
            "fundamentals.roe",
            "macro.rbi_rates"  # Doesn't analyze RBI policy
        ]
    },
    "macro_agent": {
        "description": "Analyzes RBI policy, VIX, inflation, currency, sector impacts",
        "required_data": [
            "macro.rbi_rates",
            "macro.india_vix",
            "macro.market_regime",
            "fundamentals.sector"  # For sector-specific impacts
        ],
        "optional_data": [
            "macro.nifty_pe",  # For valuation context
            "fundamentals.pe_ratio"  # For stock vs market valuation
        ],
        "irrelevant_data": [
            "price_history",  # Doesn't analyze charts!
            "sentiment.headlines",  # Doesn't analyze news
            "fundamentals.roe",  # Doesn't need detailed financials
            "fundamentals.profit_margin"
        ]
    },
    "regulatory_agent": {
        "description": "Analyzes SEBI/RBI regulations, compliance, litigations",
        "required_data": [
            "fundamentals.sector",  # Different regulations per sector
            "fundamentals.industry"
        ],
        "optional_data": [
            "sentiment.announcements",  # Corporate announcements
            "supabase_data.scores.quality_score"
        ],
        "irrelevant_data": [
            "price_history",  # Doesn't analyze charts
            "fundamentals.pe_ratio",  # Doesn't analyze valuation
            "macro.india_vix",  # Doesn't analyze market sentiment
            "sentiment.headlines"  # Doesn't analyze news
        ]
    }
}


def get_nested(data, path):
    """Get nested value from dict using dot notation."""
    keys = path.split(".")
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value


def analyze_agent_data(agent_name, agent_data, requirements):
    """Analyze data quality for a single agent."""
    results = {
        "agent": agent_name,
        "data_size_chars": len(json.dumps(agent_data, default=str)),
        "required_present": [],
        "required_missing": [],
        "required_null": [],
        "optional_present": [],
        "optional_missing": [],
        "irrelevant_present": []
    }
    
    # Check required fields
    for field_path in requirements.get("required_data", []):
        value = get_nested(agent_data, field_path)
        if value is None:
            results["required_null"].append(field_path)
        elif get_nested(agent_data, field_path.split(".")[0]) is None:
            results["required_missing"].append(field_path)
        else:
            results["required_present"].append(field_path)
    
    # Check optional fields
    for field_path in requirements.get("optional_data", []):
        value = get_nested(agent_data, field_path)
        if value is not None:
            results["optional_present"].append(field_path)
        else:
            results["optional_missing"].append(field_path)
    
    # Check irrelevant fields (should NOT be present)
    for field_path in requirements.get("irrelevant_data", []):
        root_key = field_path.split(".")[0]
        if root_key in agent_data and agent_data[root_key]:
            # Check if it has actual data (not just empty/error)
            root_value = agent_data.get(root_key)
            if isinstance(root_value, dict):
                if "error" not in root_value and root_value:
                    results["irrelevant_present"].append(field_path)
            elif isinstance(root_value, list) and len(root_value) > 0:
                results["irrelevant_present"].append(field_path)
    
    return results


def run_comprehensive_audit(ticker="IRCTC"):
    """Run comprehensive audit of all agents with real data."""
    
    print(f"🔍 COMPREHENSIVE AGENT DATA AUDIT - {ticker}")
    print("=" * 80)
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Initialize orchestrator
    orch = NiftyAgentOrchestrator()
    
    # Gather real production data
    print(f"\n1. Fetching REAL data for {ticker}...")
    base_data = orch._gather_base_data(ticker)
    
    base_size = len(json.dumps(base_data, default=str))
    print(f"   ✓ Base data size: {base_size:,} chars")
    
    # Show raw data structure
    print(f"\n2. BASE DATA STRUCTURE:")
    print("-" * 40)
    for key in base_data.keys():
        value = base_data[key]
        if isinstance(value, dict):
            size = len(json.dumps(value, default=str))
            has_error = "error" in str(value).lower()[:100]
            status = "⚠️ ERROR" if has_error else "✓"
            print(f"   {status} {key}: {size:,} chars")
        elif isinstance(value, list):
            print(f"   ✓ {key}: {len(value)} items")
        else:
            print(f"   ✓ {key}: {value}")
    
    # Check for NULL/error in critical fields
    print(f"\n3. CRITICAL FIELD STATUS:")
    print("-" * 40)
    critical_checks = [
        ("macro.india_vix.value", "VIX value for fear/greed analysis"),
        ("macro.nifty_pe", "Nifty PE for market valuation"),
        ("macro.nifty_pb", "Nifty PB for market valuation"),
        ("fundamentals.pe_ratio", "Stock PE ratio"),
        ("fundamentals.roe", "Return on Equity"),
        ("sentiment.sentiment_score", "Sentiment score"),
        ("supabase_data.scores.composite_score", "Composite score")
    ]
    
    for field_path, description in critical_checks:
        value = get_nested(base_data, field_path)
        if value is None:
            print(f"   ❌ {field_path}: NULL - {description}")
        elif isinstance(value, dict) and "error" in value:
            print(f"   ⚠️ {field_path}: ERROR - {value.get('error', 'Unknown')}")
        else:
            print(f"   ✅ {field_path}: {value}")
    
    # Analyze each agent
    print(f"\n4. PER-AGENT DATA ANALYSIS:")
    print("=" * 80)
    
    all_results = {}
    
    for agent_name, requirements in AGENT_REQUIREMENTS.items():
        print(f"\n{'='*40}")
        print(f"📊 {agent_name.upper()}")
        print(f"{'='*40}")
        print(f"Purpose: {requirements['description']}")
        
        # Get what the agent currently receives
        agent_data = orch._get_agent_specific_data(agent_name, base_data)
        agent_size = len(json.dumps(agent_data, default=str))
        
        # Analyze
        results = analyze_agent_data(agent_name, agent_data, requirements)
        all_results[agent_name] = results
        
        print(f"\nData Size: {agent_size:,} chars (base was {base_size:,})")
        print(f"Reduction: {((base_size - agent_size) / base_size * 100):.1f}%")
        
        # Required fields
        if results["required_null"]:
            print(f"\n❌ REQUIRED BUT NULL ({len(results['required_null'])}):")
            for field in results["required_null"]:
                print(f"   - {field}")
        
        if results["required_missing"]:
            print(f"\n❌ REQUIRED BUT MISSING ({len(results['required_missing'])}):")
            for field in results["required_missing"]:
                print(f"   - {field}")
        
        if results["required_present"]:
            print(f"\n✅ Required Present: {len(results['required_present'])}/{len(requirements['required_data'])}")
        
        # Irrelevant fields (should NOT be present)
        if results["irrelevant_present"]:
            print(f"\n⚠️ IRRELEVANT DATA PRESENT ({len(results['irrelevant_present'])}):")
            for field in results["irrelevant_present"]:
                print(f"   - {field} (SHOULD NOT BE SENT)")
        
        # Show actual data keys
        print(f"\nActual Data Keys: {list(agent_data.keys())}")
    
    # Summary
    print(f"\n{'='*80}")
    print("5. SUMMARY OF ISSUES")
    print("=" * 80)
    
    total_issues = 0
    for agent_name, results in all_results.items():
        issues = len(results["required_null"]) + len(results["required_missing"]) + len(results["irrelevant_present"])
        if issues > 0:
            print(f"\n{agent_name}:")
            if results["required_null"]:
                print(f"   ❌ {len(results['required_null'])} required fields are NULL")
            if results["required_missing"]:
                print(f"   ❌ {len(results['required_missing'])} required fields are MISSING")
            if results["irrelevant_present"]:
                print(f"   ⚠️ {len(results['irrelevant_present'])} irrelevant fields being sent")
            total_issues += issues
    
    if total_issues == 0:
        print("\n✅ No issues found!")
    else:
        print(f"\n🚨 TOTAL ISSUES: {total_issues}")
    
    # Save results
    output_file = "agent_data_audit_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "base_data_size": base_size,
            "agent_results": all_results,
            "base_data_keys": list(base_data.keys())
        }, f, indent=2, default=str)
    
    print(f"\n💾 Full results saved to: {output_file}")
    
    return all_results


if __name__ == "__main__":
    run_comprehensive_audit("IRCTC")
