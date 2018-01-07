set RDSHOST="rdsmysql.cdgmuqiadpid.us-west-2.rds.amazonaws.com"
set TOKEN=aws rds generate-db-auth-token --hostname %RDSHOST% --port 3306 --region eu-west-2 --username admi