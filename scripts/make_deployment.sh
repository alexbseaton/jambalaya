# Run from the scripts directory with:
# chmod u+x make_deployment.sh
# ./make_deployment.sh
set -e # fail on first error

echo Creating deployment directory
mkdir deployment

echo Installing dependencies
touch deployment_requirements.txt
pip-compile --output-file deployment_requirements.txt ../deployment_requirements.in
pip install -r deployment_requirements.txt -t ../deployment
rm deployment_requirements.txt

echo Adding handler to deployment
cp ../src/handler.py deployment

echo Zipping deployment
7z a deployment/deployment-zip.zip deployment/*

echo Pushing to AWS
aws lambda update-function-code --function-name my_function --zip-file fileb://./deployment/deployment-zip.zip
rm -r deployment
