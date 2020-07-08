import sys
import os
from functools import wraps


def insert_repo(handler):
    @wraps(handler)
    def wrapper(event, context):
        print("Event and context in insert_repo: ")
        print(event)
        print(context)
        sys.path.append('base_storage')
        sys.path.append('dynamodb_storage')
        from dynamodb_storage.dynamodb_repository import Respository

        try:
            context.user_id = event['enhancedAuthContext']['user_id']
        except:
            context.user_id = event['requestContext']['authorizer']['user_id']
        context.repository = Respository(context.user_id, os.environ['STAGE'])

        return handler(event, context)

    return wrapper
