"""Quick check of agent data fields."""
import sys
sys.path.insert(0, '.')
from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator

orch = NiftyAgentOrchestrator()
base_data = orch._gather_base_data('IRCTC')

print('--- TECHNICAL AGENT ---')
tech_data = orch._get_agent_specific_data('technical_agent', base_data)
print('volume:', tech_data.get('volume'))
print('sma50:', tech_data.get('indicators', {}).get('sma50'))
print('market_regime:', tech_data.get('market_regime'))

print('')
print('--- SENTIMENT AGENT ---')
sent_data = orch._get_agent_specific_data('sentiment_agent', base_data)
print('sector:', sent_data.get('sector'))
print('market_regime:', sent_data.get('market_regime'))
print('india_vix:', sent_data.get('india_vix'))

print('')
print('--- MACRO AGENT ---')
macro_data = orch._get_agent_specific_data('macro_agent', base_data)
print('sector:', macro_data.get('sector'))
print('pe_ratio:', macro_data.get('pe_ratio'))
print('industry:', macro_data.get('industry'))

print('')
print('--- REGULATORY AGENT ---')
reg_data = orch._get_agent_specific_data('regulatory_agent', base_data)
print('sector:', reg_data.get('sector'))
print('industry:', reg_data.get('industry'))
