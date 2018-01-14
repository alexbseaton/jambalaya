# Only useful on the ec2 cron job
cd /home/ubuntu/jambalaya
git checkout dev
git pull
pipenv install --ignore-pipfile
pipenv run python src/handler.py