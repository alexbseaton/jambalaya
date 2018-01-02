# jambalaya

# Current Goal
Draw a graph of price over time using data from RDS

## Installation
For pinning dependencies, use pip-tools:

*pip install pip-tools*

To use it:

1. Update the requirements.in file. It should contain a list of all packages imported in the code.
2. Run *pip-compile requirements.in* to compile a requirements.txt file
   that lists all the packages in requirements.in **and their dependencies**.
3. Run *pip-sync requirements.txt* to update your local environment.

# Deployment Installation - Manual
1. Run *pip-compile deployment_requirements.in*
2. Run *pip install -r deployment_requirements.txt -t deployment*

    - Note: you cannot use pip-sync here, so surplus packages will not be uninstalled.

3. Add handler.py to the deployment folder
4. Zip the *contents* of the deployment folder and put that ZIP on AWS.
5. Configure the aws command line interface

# Deployment Installation - Automated
- Run *make_deployment.cmd*
- Note: you must have pip installed in your environment
- Note: you must have the programme 7zip installed at C:\Program Files\7-Zip\7z.exe
- Note: your AWS account details must be saved as the default profile in the AWS CLI
- Note: the script currently deletes the deployment folder and starts fresh by re-downloading all
  packages. This could probably be avoided.

# Developer Installation
1. Activate your jambalaya environment
2. Run *pip-compile dev_requirements.in*
3. Run *pip-sync dev_requirements.txt*

# Notes to self
Use the named accounts (not the root) and make sure the location is London (eu-west-2) or the Lambda might go missing, which would be sad.
