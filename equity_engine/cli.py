import argparse
from .pipeline import run_pipeline_fresh

def main():
    p = argparse.ArgumentParser(description="Equity Engine: refresh Excel with metrics and composite scores.")
    p.add_argument("--template", type=str, required=True, help="Path to template workbook (v2 or later).")
    p.add_argument("--out", type=str, default=None, help="Output directory path (optional - will create month-based folder if not specified).")
    args = p.parse_args()
    run_pipeline_fresh(args.template, args.out)

if __name__ == "__main__":
    main()
