aws lambda invoke \
--invocation-type RequestResponse \
--function-name my_function \
--region eu-west-2 \
--log-type Tail \
--payload '{"key1":"value1", "key2":"value2", "key3":"value3"}' \
lambdaoutput.txt 