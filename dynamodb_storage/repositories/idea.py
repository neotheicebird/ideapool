from base import BaseRepository
from base_storage.repo_interfaces.idea import IdeaRepositoryInterface
import os
from boto3.dynamodb.conditions import Key, Attr


class IdeaRepository(BaseRepository, IdeaRepositoryInterface):
    def __init__(self, user_id, stage='dev'):
        super().__init__(
            author=user_id,
            stage=stage,
            obj_type='idea',
            required_fields=[
                'content',
                'impact',
                'ease',
                'confidence'
            ],
            endpoint_url=os.getenv("DYNAMO_ENDPOINT", None)
        )

    def get_items_by_page_number(self, user_id, page):
        key = Key('user_id').eq(user_id)
        filter_conditions = Attr('obj_type').eq('idea')

        exclusive_start_key = None
        for p in range(page):
            resp = self.db.get_objs(key=key,
                                    index_name='by_user_id_and_version',
                                    filter_conditions=filter_conditions,
                                    limit=10,
                                    exclusive_start_key=exclusive_start_key)
            print('get ideas resp')
            print(resp)
            if resp and 'LastEvaluatedKey' in resp:
                exclusive_start_key = resp['LastEvaluatedKey']
            else:
                break

        if resp and "Items" in resp:
            return resp["Items"]
        else:
            return []

