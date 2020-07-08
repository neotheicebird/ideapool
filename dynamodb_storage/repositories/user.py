from base import BaseRepository
from base_storage.repo_interfaces.user import UserRepositoryInterface
import os


class UserRepository(BaseRepository, UserRepositoryInterface):
    def __init__(self, user_id, stage='dev'):
        super().__init__(
            author=user_id,
            stage=stage,
            obj_type='user',
            required_fields=[
                'name',
                'email'
            ],
            endpoint_url=os.getenv("DYNAMO_ENDPOINT", None)
        )
