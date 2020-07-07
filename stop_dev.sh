fuser -k 8000/tcp
fuser -k 5000/tcp
fuser -k 4000/tcp
fuser -k 7000/tcp
# removing all dynamodb-local containers
docker rm $(docker stop $(docker ps -a -q --filter ancestor=amazon/dynamodb-local --format="{{.ID}}"))