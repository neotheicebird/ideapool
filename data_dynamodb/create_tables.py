from bloop import Engine
import json
import click
import boto3
from dynamodb_local_patch import patch_engine
from model import IdeaPool


def get_config(stage):
    with open('config.{STAGE}.json'.format(STAGE=stage), 'rt') as fp:
        config = json.load(fp)

    return config


@click.command()
@click.option("--stage", default='dev', help="Environment name.")
@click.option("--db_endpoint", default=None, help="Dynamodb endpoint URL")
def create_tables(stage, db_endpoint):
    print(stage, db_endpoint)
    try:
        region = get_config(stage)['REGION']
    except KeyError:
        raise Exception('REGION missing in config.{STAGE}.json'.format(STAGE=stage))

    if db_endpoint:
        client = boto3.client("dynamodb",
                              endpoint_url=db_endpoint)
        print(client)
        engine = patch_engine(Engine(dynamodb=client))
    else:
        client = boto3.client("dynamodb", region_name=region)
        engine = Engine(dynamodb=client)

    IdeaPool.Meta.table_name = IdeaPool.Meta.table_name.format(STAGE=stage)
    engine.bind(IdeaPool)


if __name__ == '__main__':
    create_tables()

