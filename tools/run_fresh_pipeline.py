"""
CLI wrapper to run a fresh pipeline output (does not modify OCT25)

Usage:
    python tools/run_fresh_pipeline.py --template Template.xlsx [--out-dir OUTDIR]

This script is intentionally minimal and won't run unless invoked explicitly.
"""
import argparse
import os
import sys

from equity_engine import pipeline


def main():
    parser = argparse.ArgumentParser(description="Run fresh equity pipeline output (safe, outside OCT25)")
    parser.add_argument("--template", required=True, help="Path to the Excel template")
    parser.add_argument("--out-dir", required=False, help="Optional output directory")
    args = parser.parse_args()

    template = args.template
    out_dir = args.out_dir

    if not os.path.exists(template):
        print(f"Template not found: {template}")
        sys.exit(2)

    final = pipeline.run_pipeline_fresh(template, out_dir=out_dir)
    print(f"Pipeline completed. Output written to: {final}")


if __name__ == "__main__":
    main()
