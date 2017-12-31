aws lambda create-function \
--region eu-west-2 \
--function-name   CreateTableAddRecordsAndRead3  \
--zip-file fileb://./deployment/deployment-zip.zip \
--role arn:aws:iam::773696806494:role/service-role/write \
--handler app.handler \
--runtime python3.6 \
--vpc-config SubnetIds=subnet-4cd5e137,subnet-8d9addc0,SecurityGroupIds=sg-86b621ee \