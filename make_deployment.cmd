@ECHO OFF


ECHO Remove old deployment
rmdir /s deployment
rm deployment-zip.zip

ECHO.

ECHO Create deployment directory
pip-compile --output-file deployment_requirements.txt deployment_requirements.in
pip install -r deployment_requirements.txt -t deployment
xcopy src\handler.py deployment
cd deployment
"C:\Program Files\7-Zip\7z.exe" a ../deployment-zip.zip *
