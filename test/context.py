import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import rds_config

# To use this you must have a database locally with these properties
rds_config.db_username = "root"
rds_config.db_password = "password"
rds_config.db_name = "jambalaya"
rds_config.rds_host = "127.0.0.1"
