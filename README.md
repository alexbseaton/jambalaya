# jambalaya

# Steps to build engine
1. Find source: Expedia
2. Scrape flight prices
3. ...

# Steps to improve repo
1. Write PEP8 test (PEP8 failures, minimal print statements)
2. Create logger
3. Decouple test and source code....


# Deployment Installation
To create a deployment package, install the requirements by running,

pip-install -r requirements.txt -t deployment_directory

then add handler.py to that folder, then zip the *contents* of the deployment folder and put that ZIP on AWS.

NOTE: this process may result in surplus requirements. Any requirements that are installed to the
deployment directory but later removed from requirements.txt will remain installed.

# Developer Installation/Maintenance
To maintain the environment, you can skip step 1
1. Install pip tools
   pip install pip-tools
2. List all and only the required packages in requirements.in
3. Compile a list of packages in requirements.in along and their dependencies
   pip-compile --output-file requirements.txt requirements.in
4. Update your environment:
   pip-sync requirements.txt

Note: this process will ensure that any packages already installed in your environment that are not
listed in requirements.in are uninstalled.
