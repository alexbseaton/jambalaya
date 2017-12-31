set -e # fail on first error

echo Creating deployment directory
mkdir deployment

echo Installing dependencies
pip3 install pymysql -t ./deployment

echo Adding python scripts to deployment
cp ../src/{app.py,rds_config.py} ./deployment

echo Zipping deployment
7z a ./deployment/deployment-zip.zip ./deployment/*