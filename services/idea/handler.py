import logging
from common import insert_repo
import json
from base_storage.exceptions import NoSuchEntity


@insert_repo
def create_idea(event, context):
    print("Event and context in idea: ")
    print(event)
    print(context)
    body = json.loads(event.get('body'))
    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': "Bad Payload"
            }),
            'headers': {'Content-Type': 'application/json'}
        }

    body["user_id"] = context.user_id

    obj = context.repository.repos['idea'].save(body)
    obj["id"] = obj.pop("entity_id")

    return {
        'statusCode': 201,
        'body': json.dumps(obj),
        'headers': {'Content-Type': 'application/json'}
    }


@insert_repo
def update_idea(event, context):
    logging.debug(event)
    logging.debug(context)
    body = json.loads(event.get('body'))
    entity_id = event.get("pathParameters")["entity_id"]

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': "Bad Payload"
            }),
            'headers': {'Content-Type': 'application/json'}
        }

    try:
        context.repository.repos['idea'].get(entity_id)
    except NoSuchEntity:
        return {
            'statusCode': 404,
            'body': json.dumps({
                "error": "No such entity"
            }),
            'headers': {'Content-Type': 'application/json'}
        }

    body["entity_id"] = entity_id
    body["user_id"] = context.user_id

    obj = context.repository.repos['idea'].save(body)

    return {
        'statusCode': 201,
        'body': json.dumps(obj),
        'headers': {'Content-Type': 'application/json'}
    }


@insert_repo
def delete_idea(event, context):
    logging.debug(event)
    logging.debug(context)
    entity_id = event.get("pathParameters")["entity_id"]
    try:
        context.repository.repos['idea'].delete(entity_id)

        return {
            'statusCode': 204
        }
    except NoSuchEntity:
        print("No such Entity")
        return {
            'statusCode': 404,
            'body': json.dumps({
                "error": "No such entity"
            }),
            'headers': {'Content-Type': 'application/json'}
        }


@insert_repo
def get_ideas(event, context):
    logging.debug(event)
    logging.debug(context)
    try:
        page = event.get("queryStringParameters")["page"]
    except:
        page = 1

    try:
        int(page)
    except ValueError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "error": "Bad query parameter"
            }),
            'headers': {'Content-Type': 'application/json'}
        }

    items = context.repository.repos['idea'].get_items_by_page_number(context.user_id, int(page))

    return {
        'statusCode': 201,
        'body': json.dumps(items),
        'headers': {'Content-Type': 'application/json'}
    }