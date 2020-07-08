from abc import ABCMeta, abstractmethod


class IdeaRepositoryInterface(metaclass=ABCMeta):
    @abstractmethod
    def get_items_by_page_number(self, user_id, page):
        pass
