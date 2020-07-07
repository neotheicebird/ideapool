import sys
sys.path.append('base_storage')

from data_interface import StorageBase
from uuid import uuid4
import maya
import boto3
from boto3.dynamodb.conditions import Key, Attr
from dynamodb_json import json_util
import json
from botocore.exceptions import ClientError


class DynamodbStorage(StorageBase):
    def __init__(self, user_id, table, endpoint_url=None):
        self._user_id = user_id
        self._table_name = table
        self._table = boto3.resource('dynamodb', endpoint_url=endpoint_url).Table(table)
        self._client = boto3.client('dynamodb', endpoint_url=endpoint_url)

    @staticmethod
    def clean(obj):
        private_attrs = ["previous_version", "changed_by_id"]
        for attr in private_attrs:
            obj.pop(attr)
        return obj

    def save(self, obj, obj_type):
        print(obj)
        old_events = []
        if "entity_id" not in obj:
            obj["entity_id"] = uuid4()
        else:
            # get latest item
            response = self._table.query(
                KeyConditionExpression=Key("entity_id").eq(obj["entity_id"]),
                Limit=24,
                ScanIndexForward=False,
                FilterExpression=Attr('read_only').not_exists() & Attr('active').eq(True)
            )
            if response["Count"] > 0:
                for old_item in response["Items"]:
                    old_item = json_util.loads(json_util.dumps(old_item))
                    old_events.append(
                        {
                            'Update': {
                                'TableName': self._table_name,
                                'Key': json.loads(json_util.dumps({
                                    'entity_id': old_item['entity_id'],
                                    'version': old_item['version']
                                })),
                                'UpdateExpression': 'set read_only = :read_only',
                                'ExpressionAttributeValues': {
                                    ':read_only': {'BOOL': True},
                                }
                            }
                        }
                    )
                print(old_events)

        if "version" in obj:
            obj["previous_version"] = obj["version"]
        else:
            obj["previous_version"] = '0000-00-00T00:00:00.000000Z' + self._user_id

        obj["version"] = maya.now().iso8601() + self._user_id
        obj["changed_by_id"] = self._user_id

        if "active" not in obj:
            obj["active"] = True

        obj["obj_type"] = obj_type

        obj = json_util.loads(json_util.dumps(obj))

        # make atomic update
        try:
            response = self._client.transact_write_items(
                TransactItems=[
                    {
                        'Put': {
                            'TableName': self._table_name,
                            'Item': json.loads(json_util.dumps(obj))
                            }
                    },
                    *old_events
                ]
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return self.clean(obj)
        except ClientError as e:
            if e.response['Error']['Code'] == 'TransactionCanceledException':
                print("TransactionCanceledException")
            else:
                print("Unexpected error: %s" % e)

        return {}

    def get(self, entity_id, attributes=None):
        if not attributes:
            response = self._table.query(
                KeyConditionExpression=Key("entity_id").eq(entity_id),
                Limit=1,
                ScanIndexForward=False,
                FilterExpression=Attr('active').eq(True),
            )
        else:
            projection_expression = ",".join(attributes)
            response = self._table.query(
                KeyConditionExpression=Key("entity_id").eq(entity_id),
                Select="SPECIFIC_ATTRIBUTES",
                ProjectionExpression=projection_expression,
                Limit=1,
                ScanIndexForward=False,
                FilterExpression=Attr('active').eq('true'),
            )
        if "Items" in response and response["Items"]:
            return self.clean(json_util.loads(json_util.dumps(response["Items"][0])))
        return None

    def get_objs(self,
                 obj_type,
                 key,
                 index_name,
                 filter_conditions=None):
        filter_by = Attr('active').eq(True) &\
                    Attr('read_only').not_exists()

        if filter_conditions:
            filter_by &= filter_conditions

        resp = self._table.query(
            KeyConditionExpression=key,
            ScanIndexForward=False,
            FilterExpression=filter_by,
            IndexName=index_name
        )

        if resp["Count"] > 0:
            return resp["Items"]
        else:
            return []

    def delete(self, entity_id):
        item = self.get(entity_id)
        if item:
            item["active"] = False    # deleting the latest item
            item["read_only"] = True    # deleting the latest item
            return self.save(item, item["obj_type"])
        return None


if __name__ == "__main__":
    storage = DynamodbStorage(user_id='prashanth',
                              table='ip-test',
                              endpoint_url="http://localhost:8000/")

    idea_1 = {
        "score": 3,
        "idea": "Make pizza in Tawa"
    }

    added_idea = storage.save(obj_type="idea",
                              obj=idea_1)

    print("getting idea after adding")
    get_idea = storage.get(added_idea["entity_id"])
    print(get_idea)

    added_idea["idea"] += "!!!"
    updated_idea = storage.save(obj_type="idea",
                                obj=added_idea)

    deleted_idea = storage.delete(entity_id=updated_idea["entity_id"])

    print("getting idea after deleting")
    get_idea = storage.get(added_idea["entity_id"])
    print(get_idea)

    idea_2 = {
        "score": 4,
        "idea": "Make Soba using rice"
    }

    added_idea = storage.save(obj_type="idea",
                              obj=idea_2)

    idea_3 = {
        "score": 4,
        "idea": "Coffee boost"
    }

    added_idea = storage.save(obj_type="idea",
                              obj=idea_3)
    print("Get all ideas")

    items = storage.get_objs(obj_type='idea',
                     index_name='by_obj_type_and_version',
                     key=Key('obj_type').eq('idea'),
                     filter_conditions=Attr('idea').begins_with("Coffee"))
    print(items)
