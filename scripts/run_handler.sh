# Only useful on the ec2 cron job
cd /home/ubuntu/jambalaya
git checkout master
git pull
pipenv run python src/handler.py