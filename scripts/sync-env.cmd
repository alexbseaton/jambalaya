pip install --upgrade pip-tools

pip-compile --output-file dev_requirements.txt ../dev_requirements.in

pip-sync dev_requirements.txt

DEL dev_requirements.txt
