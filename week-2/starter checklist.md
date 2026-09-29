
### Starter 

pip install --break-system-packages fastapi==0.115.6 httpx==0.28.1

cd 

uv venv .venv --python 3.12

source .venv/bin/activate

uv pip install --python .venv/bin/python -r requirements.txt

uv pip list --python .venv/bin/python

PYTHONPATH=src .venv/bin/python -m uvicorn main:app --reload


#### The main rule when translating those instructions is:

Windows: .venv/Scripts/python.exe

Mac: .venv/bin/python


### ANTHROPIC API KEY 

export ANTHROPIC_API_KEY="YOUR_NEW_KEY"

python -c "import os; print('key present:', bool(os.environ.get('ANTHROPIC_API_KEY')))"

You want:
"key present: True"

.venv/bin/python -m ensurepip --upgrade

.venv/bin/python -m pip --version

.venv/bin/python -m pip install anthropic

.venv/bin/python -c "import anthropic; print('Anthropic SDK installed')"
