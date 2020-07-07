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

    obj_type = Column(String)

    by_obj_type_and_version = GlobalSecondaryIndex(
        projection='all',
        hash_key='obj_type',
        range_key='version',
    )
