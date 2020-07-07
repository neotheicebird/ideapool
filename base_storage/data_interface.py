from abc import ABCMeta, abstractmethod


class StorageBase(metaclass=ABCMeta):
    @abstractmethod
    def save(self, obj, obj_type):
        pass

    @abstractmethod
    def get(self, entity_id):
        pass

    @abstractmethod
    def delete(self, entity_id):
        pass
