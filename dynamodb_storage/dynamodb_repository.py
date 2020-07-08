import os
import sys

src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(src_path)

from dynamodb_storage.repositories.idea import IdeaRepository
from dynamodb_storage.repositories.user import UserRepository


class Respository:
    def __init__(self, user_id, stage):
        self.repos = {
            'idea': IdeaRepository(user_id, stage),
            'user': UserRepository(user_id, stage),
        }


if __name__ == '__main__':
    import os
    os.environ['DYNAMO_ENDPOINT'] = "http://localhost:8000"
    repository = Respository('prashanth', 'test')
    obj = repository.repos['idea'].save({
        'content': 'Pizza in tawa!',
        'impact': 7,
        'ease': 9,
        'confidence': 5,
    })
    print("Saved: ")
    print(obj)

    get_obj = repository.repos['idea'].get(obj["entity_id"])
    print("Got: ")
    print(get_obj)

    get_obj["confidence"] = 6
    updated_obj = repository.repos['idea'].save(get_obj)
    print("Updated: ")
    print(updated_obj)

    deleted_obj = repository.repos['idea'].delete(updated_obj["entity_id"])
    print("Deleted: ")
    print(deleted_obj)

