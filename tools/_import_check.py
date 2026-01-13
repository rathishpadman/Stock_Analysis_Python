import importlib

try:
    m = importlib.import_module('equity_engine.pipeline')
    print('Imported equity_engine.pipeline OK')
    print('run_pipeline_fresh exists:', hasattr(m, 'run_pipeline_fresh'))
except Exception as e:
    print('Import failed:', e)
