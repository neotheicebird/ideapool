from bloop import (
    BaseModel, Boolean, Column, Number,
    GlobalSecondaryIndex, String, UUID)


class IdeaPool(BaseModel):
    class Meta:
        table_name = "ip-{STAGE}"
        billing = {
            "mode": "on_demand"
        }

    entity_id = Column(UUID, hash_key=True)
    version = Column(String, range_key=True)

    user_id = Column(String)

    by_user_id_and_version = GlobalSecondaryIndex(
        projection='all',
        hash_key='user_id',
        range_key='version',
    )
