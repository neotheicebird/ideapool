## Quickstart

```shell script
sh stop_dev.sh  # stops any running processes used in local development
sh run_dev.sh   # runs processes like dynamodb-local
pipenv shell    # starts shell
python data_dynamodb/create_tables.py --stage test --db_endpoint http://localhost:8000
```

## Create tables

`python data_dynamodb/create_tables.py --stage test`

where `test` is the stage name and a corresponding `config.test.json` should be found in the parent directory.

## References:

Custom Authorizers: [https://www.alexdebrie.com/posts/lambda-custom-authorizers/](https://www.alexdebrie.com/posts/lambda-custom-authorizers/)

