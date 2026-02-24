"""Run Alembic migrations using Flask-Migrate.

This script will initialize the migrations repository (if missing),
create an initial migration, and apply it (upgrade to head).

Usage:
  python run_migrations.py
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
MIGRATIONS_DIR = ROOT / 'migrations'

# Ensure Flask app entrypoint
os.environ.setdefault('FLASK_APP', 'run.py')

def run(cmd):
    print('> ' + cmd)
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"Command failed with exit code {res.returncode}")
        sys.exit(res.returncode)

if __name__ == '__main__':
    # Use project root as working dir
    cwd = str(ROOT)

    # Create migrations folder if missing
    if not MIGRATIONS_DIR.exists():
        print('Initializing migrations repository...')
        run('flask db init')

    print('Generating migration...')
    run('flask db migrate -m "initial migration"')

    print('Applying migration (upgrade head)...')
    run('flask db upgrade')

    print('\n✓ Migrations completed successfully.')
