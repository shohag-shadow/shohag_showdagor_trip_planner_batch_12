set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
if [ ! -d "instance" ]; then
    mkdir instance
fi
if [ ! -f .env ]; then
    cp .env.example .env
fi
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest test.py -v
exec .venv/bin/python run.py