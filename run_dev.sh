docker run -p 8000:8000 amazon/dynamodb-local &
export DYNAMO_ENDPOINT=http://localhost:8000
dynamodb-admin -p 7000 &
