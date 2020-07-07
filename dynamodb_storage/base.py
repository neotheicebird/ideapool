from dynamodb_storage.dynamodb_adapter import DynamodbStorage
from base_storage.exceptions import MissingRequiredField, NoSuchEntity
from base_storage.base_repo_interface import BaseRepositoryInterface


class BaseRepository(BaseRepositoryInterface):
    def __init__(self, author, stage, obj_type, required_fields, endpoint_url=None):
        if endpoint_url:
            self.db = DynamodbStorage(
                user_id=author,
                table=f'ip-{stage}',
                endpoint_url=endpoint_url
            )
        else:
            self.db = DynamodbStorage(
                user_id=author,
                table=f'ip-{stage}'
            )
        self.obj_type = obj_type
        self.required_fields = required_fields

    def save(self, obj):
        for field in self.required_fields:
            if field not in obj:
                raise MissingRequiredField

        return self.db.save(obj, self.obj_type)

    def get(self, entity_id):
        entity = self.db.get(entity_id)
        if entity:
            return entity
        else:
            raise NoSuchEntity

    def delete(self, entity_id):
        entity = self.db.delete(entity_id)
        if entity:
            return entity
        else:
            raise NoSuchEntity


# repo['profile'].save(obj)
# repo['profile'].get(entity_id)
# repo('profile').delete(entity_id)
# repo('profile').get_items()