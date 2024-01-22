from abc import abstractmethod, ABC, ABCMeta
from contextlib import contextmanager
from typing import Protocol

entity_repo_classes = {}

class EntityRepoMeta(ABCMeta):
    def __init__(cls, name, bases, dict):
        if ABC not in bases:
            print("Registering Repo Class: ", cls, name, bases)
            # TODO: How do we want to handle namespacing repos for entities with same name, across Feature collections
            entity_repo_classes[cls.ENTITY_CLS.__name__] = cls


class EntityRepo(ABC, metaclass=EntityRepoMeta):
    def __init__(self, db_session):
        self.db_session = db_session

    @classmethod
    @property
    @abstractmethod
    def ENTITY_CLS(cls):
        raise NotImplementedError

    @classmethod
    @property
    @abstractmethod
    def DATA_STORE_TYPE(cls):
        raise NotImplementedError

    def init_db_session(db_session):
        self.db_session = db_session

    def clear_db_session(db_session):
        self.db_session = None


class EntityRepoManager:
    repo_types = entity_repo_classes
    # TODO:  How do we handle caching 
    # TODO: How do we handle optimistic concurrency
    def __init__(self):
        self.repo_instances = {}
        self.session_getters_by_data_source_type = {}

    def __getitem__(self, entity_name):
        # TODO:(Hristo) Add exception for missing/ unregistered repo
        repo_type = self.repo_types[entity_name]
        if repo_type in self.repo_instances:
            repo_instance = self.repo_instances[repo_type]
            print("DB using existing session")
        else:
            session = self.session_getters_by_data_source_type[repo_type.DATA_STORE_TYPE]()
            session.begin()
            repo_instance = repo_type(session)
            print("DB Session start", session)
            self.repo_instances[repo_type] = repo_instance

        return repo_instance
    
    @contextmanager
    def init_session(self, with_commit=True):
        try:
            yield self
        finally:
            for repo in self.repo_instances.values():
                repo.db_session.commit()
                if with_commit:
                    repo.db_session.close()
                print("DB Session end", repo.db_session)

            repo_instances = {}

    def update_mutated(self):
        # TODO: How do we handle tracking "dirtied/ mutated" entities
        pass
