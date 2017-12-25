rm -r deployment
rm deployment-zip.zip

echo

echo Create deployment directory

pip-compile --output-file deployment_requirements.txt deployment_requirements.in
pip install -r deployment_requirements.txt -t deployment
rm deployment_requirements.txt
cp src/handler.py deployment
zip deployment/deployment-zip.zip deployment/*

aws s3 cp deployment/deployment-zip.zip s3://alex-jambalaya-json-dumps
aws lambda update-function-code --function-name my_function --s3-bucket alex-jambalaya-json-dumps --s3-key deployment-zip.zip
