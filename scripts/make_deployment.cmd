@ECHO OFF


ECHO Remove old deployment
rmdir /s ..\deployment

ECHO.

ECHO Create deployment directory
pip-compile --output-file deployment_requirements.txt ../deployment_requirements.in
pip install -r deployment_requirements.txt -t ../deployment
DEL deployment_requirements.txt

xcopy ..\src\handler.py ..\deployment
xcopy ..\src\scrape_parser.py ..\deployment
xcopy ..\src\rds_config.py ..\deployment
"C:\Program Files\7-Zip\7z.exe" a ../deployment/deployment-zip.zip ../deployment/*


REM aws s3 rm s3://alex-jambalaya-json-dumps/deployment-zip.zip
REM aws s3 cp ..\deployment\deployment-zip.zip s3://alex-jambalaya-json-dump

aws lambda update-function-code --function-name my_function --zip-file fileb://../deployment/deployment-zip.zip
