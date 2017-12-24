rmdir /s deployment
y
@ECHO OFF
ECHO.
ECHO Create deployment directory
REM C:\Anaconda3\Scripts\pip.exe
pip-compile --output-file deployment_requirements.txt deployment_requirements.in
pip install -r deployment_requirements.txt -t deployment
xcopy src\handler.py deployment
