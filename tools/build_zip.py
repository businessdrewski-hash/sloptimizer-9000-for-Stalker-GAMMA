"""Build an MO2-installable source package using only Python's standard library."""
from pathlib import Path
import argparse
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=ROOT.parent / 'Sloptimizer-9000-2.10.1-readable.zip')
args = parser.parse_args()
files = [ROOT / 'README.md']
for directory in ('gamedata', 'docs', 'tests', 'review', 'tools', 'assets', 'benchmarks'):
    files.extend(p for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
args.output.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted(files):
        # Stable metadata makes repeated builds from identical files reproducible.
        info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(2026, 11, 7, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, path.read_bytes())
with zipfile.ZipFile(args.output) as archive:
    assert archive.testzip() is None
    for path in files:
        assert archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes()
print(args.output)
print('SHA256:', hashlib.sha256(args.output.read_bytes()).hexdigest())
