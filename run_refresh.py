#!/usr/bin/env python3
import os
import sys
from equity_engine.cli import main
import logging
if __name__ == "__main__":
    # Allow running as: python run_refresh.py --template path --out path
    main()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),                       # console
        logging.FileHandler("equity_engine_debug.log", encoding="utf-8")  # file in CWD
    ]
)