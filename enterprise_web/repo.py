from abc import abstractmethod, ABC, ABCMeta
from contextlib import contextmanager
from enum import Enum
from typing import Any, Callable, Generic, Protocol, TypeVar

_entity_repo_classes = {}
_data_store_session_getters = {}

class Entity(ABC):
    pass

GenericEntity = TypeVar('GenericEntity', bound=Entity)

EntityIDInt = int
EntityIDStr = str

class DataStoreSession(Protocol):
    # TODO: (Hristo) how do we correctly type annotate a generic data store session
    def begin(self, *args, **kwargs) -> Any:
        pass

    def commit(self, *args, **kwargs) -> Any:
        pass

    def close(self, *args, **kwargs) -> Any:
        pass

DataStoreSessionGetter = Callable[[], DataStoreSession]

def register_session_getter(session_type: Enum):
    def build_decorator(f: DataStoreSessionGetter):
        _data_store_session_getters[session_type] = f
        return f
    return build_decorator

class RepoErrorMissingEntityClass(Exception):
    pass

class RepoErrorMissingDataStoreType(Exception):
    pass

class EntityRepoType(Protocol, Generic[GenericEntity]):
    ENTITY_CLS: type[GenericEntity]
    DATA_STORE_TYPE: Enum

    def __init__(self, name, bases, attr_dict: Any):
        pass

class EntityRepoMeta(ABCMeta):
    def __init__(cls: EntityRepoType, name, bases, attr_dict):
        if ABC not in bases:
            print("Registering Repo Class: ", cls, name, bases)
            # TODO: (Hristo) How do we want to handle namespacing repos for entities with same name,
            # TODO: (Hristo) across Feature collections

            if not cls.ENTITY_CLS:
                raise RepoErrorMissingEntityClass

            if not cls.DATA_STORE_TYPE:
                raise RepoErrorMissingDataStoreType

            _entity_repo_classes[cls.ENTITY_CLS.__name__] = cls

            super().__init__(name, bases, attr_dict)


class MissingRetriverIdsParam(Exception):
    pass

class EntityRepo(ABC, Generic[GenericEntity], metaclass=EntityRepoMeta):
    ENTITY_CLS: type[GenericEntity]
    DATA_STORE_TYPE: Enum

    def __init__(self, db_session):
        self.db_session = db_session
        self._tracked_entities: dict[Any, GenericEntity] = {}

    @staticmethod
    def entity_retriver(f):
        import inspect
        print(inspect.get_annotations(f))
        method_annotations = inspect.get_annotations(f)

        ids_param_name = None
        for name, type_ in method_annotations.items():
            if type_ in [list[EntityIDStr], list[EntityIDInt]]:
                ids_param_name = name
                break

        if not ids_param_name:
            raise MissingRetriverIdsParam

        print(ids_param_name)

        def wrapped(*args, **kwargs):
            # TODO: (Hristo) Related to updating/saving mutated Ents. and caching
            # TODO: (Hristo) Do we use add, get, update/save methods instead ? 
            # TODO: (Hristo) Bulkk_update/save ?
            return f # Return f for now so current version keeps working
            
        return wrapped


class EntityRepoManager:
    repo_types = _entity_repo_classes
    session_getters_by_data_source_type = _data_store_session_getters
    # TODO: (Hristo) How do we handle caching/ returning same Ent. obj across session
    # TODO: (Hristo) How do we handle optimistic concurrency
    def __init__(self):
        self.repo_instances = {} # TODO: (Hristo) these should go on a repo session object

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
        # TODO: (Hristo) Should be creating a repo session here and using it to store instance to allow creating
        # TODO: (Hristo) session outside of web hander dep. injection
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
        # TODO: (Hristo) How do we handle tracking "dirtied/ mutated" entities, do we want this as part of framework

        pass
