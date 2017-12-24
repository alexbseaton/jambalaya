# jambalaya

# Steps to build engine
1. Find source: Expedia
2. Scrape flight prices
3. ...

# Steps to improve repo
1. Write PEP8 test (PEP8 failures, minimal print statements)
2. Create logger
3. Decouple test and source code....

## Installation
For pinning dependencies, we use pip-tools:

pip install pip-tools

Pip-tools allows you to ensure that your local environment contains *exactly* packages specified in the requirements file. In general, the usage of pip-tools is:

1. Update the requirements.in file. It should contain a list of all packages imported in the code.
2. Run *pip-compile --output-file requirements.txt requirements.in* to compile a requirements file
   that lists all the packages in requirements.in **and their dependencies**.
3. Run *pip-sync requirements.txt* to update your local environment.

# Deployment Installation
1. Run *pip-compile --output-file deployment_requirements.txt deployment_requirements.in*
2. Run *pip install -r deployment_requirements.txt -t deployment*

  - Note: you cannot use pip-sync here, so surplus packages will not be uninstalled.

3. Add handler.py to the deployment folder, then zip the *contents* of the deployment folder and
   put that ZIP on AWS.

# Developer Installation
1. Activate your jambalaya environment
2. Run *pip-compile --output-file dev_requirements.txt dev_requirements.in*
3. Run *pip-sync dev_requirements.txt*
