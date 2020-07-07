from abc import ABCMeta, abstractmethod


class BaseRepositoryInterface(metaclass=ABCMeta):
    @abstractmethod
    def save(self, obj):
        pass

    @abstractmethod
    def get(self, entity_id):
        pass

    @abstractmethod
    def delete(self, entity_id):
        pass
