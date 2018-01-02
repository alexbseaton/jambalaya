# Run from the scripts directory with:
# chmod u+x make_deployment.sh
# ./make_deployment.sh
set -e # fail on first error

echo Creating deployment directory
mkdir deployment

echo Installing dependencies
pip3 install -r ../deployment_requirements.in -t ./deployment

echo Adding python scripts to deployment
cp ../src/{handler.py,leg.py,rds_config.py} ./deployment

echo Zipping deployment
7z a ./deployment/deployment-zip.zip ./deployment/*

echo Pushing to AWS
aws lambda update-function-code --function-name my_function --zip-file fileb://./deployment/deployment-zip.zip
rm -r deployment
