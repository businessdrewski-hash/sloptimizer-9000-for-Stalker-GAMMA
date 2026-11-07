"""Portable checks; does not launch or alter the game."""
from pathlib import Path
import subprocess,sys
for name in ('test_optional_mods.py','test_diagnostics.py','test_split_modules.py','test_lamp_saves.py'):
 subprocess.run([sys.executable,str(Path(__file__).resolve().parent/name)],check=True)
print('All portable checks passed.')
