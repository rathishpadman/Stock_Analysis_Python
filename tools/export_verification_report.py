"""Export a verification CSV from the latest backups/normalized_<ts>/ workbook.

Reads the Normalization_Provenance sheet and writes a CSV report into the same
normalized folder along with a short summary printed to stdout.
"""
import pathlib
import pandas as pd
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
backups = ROOT / 'backups'

def find_latest_normalized_folder():
    dirs = [d for d in backups.glob('normalized_*') if d.is_dir()]
    if not dirs:
        return None
    dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return dirs[0]

def find_normalized_workbook(folder: pathlib.Path):
    files = list(folder.glob('*_normalized_*.xlsx'))
    if not files:
        return None
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0]

def run():
    folder = find_latest_normalized_folder()
    if folder is None:
        print('No normalized backups found')
        return 2
    wb = find_normalized_workbook(folder)
    if wb is None:
        print('No normalized workbook found in', folder)
        return 2
    print('Using normalized workbook:', wb)
    xl = pd.ExcelFile(wb)
    if 'Normalization_Provenance' not in xl.sheet_names:
        print('No Normalization_Provenance sheet in workbook')
        return 2
    prov = xl.parse('Normalization_Provenance')
    out_csv = folder / 'verification_report.csv'
    prov.to_csv(out_csv, index=False)
    print('Wrote verification report to:', out_csv)
    print('Total changes:', len(prov))
    # print top 5 changes
    print('\nTop 5 changes:')
    print(prov.head().to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(run())
