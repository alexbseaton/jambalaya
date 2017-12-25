@ECHO OFF


ECHO Remove old deployment
rmdir /s ..\deployment

ECHO.

ECHO Create deployment directory
pip-compile --output-file deployment_requirements.txt ../deployment_requirements.in
pip install -r deployment_requirements.txt -t ../deployment
DEL deployment_requirements.txt

xcopy ../src\handler.py ../deployment
"C:\Program Files\7-Zip\7z.exe" a ../deployment/deployment-zip.zip ../deployment/*

aws s3 cp ../deployment/deployment-zip.zip s3://alex-jambalaya-json-dumps
aws lambda update-function-code --function-name my_function --s3-bucket alex-jambalaya-json-dumps --s3-key deployment-zip.zip
