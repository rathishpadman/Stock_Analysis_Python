"""
Quick verification of fixed agent data allocation.
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator

def verify_all_agents(ticker="IRCTC"):
    """Verify each agent gets correct data."""
    print(f"🔍 VERIFYING ALL AGENTS - {ticker}")
    print("=" * 80)
    
    orch = NiftyAgentOrchestrator()
    
    # Get real data
    print(f"\n1. Fetching REAL data for {ticker}...")
    base_data = orch._gather_base_data(ticker)
    base_size = len(json.dumps(base_data, default=str))
    print(f"   Base data size: {base_size:,} chars")
    
    # Check each agent
    agents = [
        "fundamental_agent",
        "technical_agent",
        "sentiment_agent", 
        "macro_agent",
        "regulatory_agent"
    ]
    
    all_passed = True
    
    for agent_name in agents:
        print(f"\n{'='*40}")
        print(f"📊 {agent_name.upper().replace('_', ' ')}")
        print(f"{'='*40}")
        
        agent_data = orch._get_agent_specific_data(agent_name, base_data)
        agent_size = len(json.dumps(agent_data, default=str))
        reduction = ((base_size - agent_size) / base_size * 100)
        
        print(f"Size: {agent_size:,} chars ({reduction:.1f}% reduction)")
        print(f"Keys: {list(agent_data.keys())}")
        
        issues = []
        
        # Check agent-specific requirements
        if agent_name == "fundamental_agent":
            checks = [
                ("fundamentals", agent_data.get("fundamentals")),
                ("fundamentals.pe_ratio", agent_data.get("fundamentals", {}).get("pe_ratio")),
                ("fundamentals.sector", agent_data.get("fundamentals", {}).get("sector")),
                ("current_price", agent_data.get("current_price")),
                ("scores", agent_data.get("scores"))
            ]
        
        elif agent_name == "technical_agent":
            checks = [
                ("price_history.data", agent_data.get("price_history", {}).get("data")),
                ("volume", agent_data.get("volume")),
                ("indicators.sma50", agent_data.get("indicators", {}).get("sma50")),
                ("current_price", agent_data.get("current_price")),
                ("market_regime", agent_data.get("market_regime"))
            ]
        
        elif agent_name == "sentiment_agent":
            checks = [
                ("sentiment", agent_data.get("sentiment")),
                ("sector", agent_data.get("sector")),
                ("india_vix", agent_data.get("india_vix")),
                ("market_regime", agent_data.get("market_regime"))
            ]
        
        elif agent_name == "macro_agent":
            checks = [
                ("macro", agent_data.get("macro")),
                ("sector", agent_data.get("sector")),
                ("industry", agent_data.get("industry")),
                ("pe_ratio", agent_data.get("pe_ratio")),
                ("macro.rbi_rates", agent_data.get("macro", {}).get("rbi_rates"))
            ]
        
        elif agent_name == "regulatory_agent":
            checks = [
                ("sector", agent_data.get("sector")),
                ("industry", agent_data.get("industry")),
                ("scores", agent_data.get("scores")),
                ("announcements", agent_data.get("announcements"))
            ]
        
        # Run checks
        for field_name, value in checks:
            if value is None:
                issues.append(f"❌ {field_name}: NULL")
            elif isinstance(value, dict) and "error" in value:
                issues.append(f"⚠️ {field_name}: ERROR - {value.get('error', '')[:50]}")
            elif isinstance(value, list) and len(value) == 0:
                issues.append(f"ℹ️ {field_name}: EMPTY list")
            else:
                if isinstance(value, list):
                    print(f"   ✅ {field_name}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"   ✅ {field_name}: {len(value)} keys")
                else:
                    val_str = str(value)[:50]
                    print(f"   ✅ {field_name}: {val_str}")
        
        # Check for irrelevant data
        if agent_name == "macro_agent":
            if "price_history" in agent_data:
                issues.append(f"⚠️ price_history: SHOULD NOT BE PRESENT")
        
        if agent_name == "fundamental_agent":
            if "price_history" in agent_data:
                issues.append(f"⚠️ price_history: SHOULD NOT BE PRESENT")
        
        if issues:
            print("\nIssues Found:")
            for issue in issues:
                print(f"   {issue}")
            all_passed = False
        else:
            print("\n✅ All checks passed!")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if all_passed:
        print("✅ ALL AGENTS PASSED - Data allocation correct!")
    else:
        print("⚠️ SOME ISSUES FOUND - Review above")
    
    return all_passed

if __name__ == "__main__":
    verify_all_agents("IRCTC")
