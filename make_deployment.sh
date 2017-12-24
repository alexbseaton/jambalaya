rm -r deployment
rm deployment-zip.zip

echo

echo Create deployment directory

pip-compile --output-file deployment_requirements.txt deployment_requirements.in
pip install -r deployment_requirements.txt -t deployment
cp src/handler.py deployment
cd deployment
zip ../deployment-zip.zip *
