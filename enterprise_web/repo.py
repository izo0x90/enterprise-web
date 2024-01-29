from abc import (
    abstractmethod,
    ABC,
    ABCMeta
)
from contextlib import contextmanager
from enum import Enum
from typing import (
    Any,
    Callable,
    MutableMapping,
    Generic,
    Mapping,
    Protocol,
    Sequence,
    TypeVar
)

from .dev import NEEDSTYPEHINT
from .log import get_logger

logger = get_logger()


_entity_repo_classes = {}
_data_store_session_getters = {}

GenericEntityId = TypeVar('GenericEntityId', int, str)

class Entity(ABC, Generic[GenericEntityId]):
    id: GenericEntityId

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
        logger.debug(f"Adding session getter: `{f}`, type: `{session_type}`")
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
            logger.debug("Registering Repo Class: ", cls, name, bases)
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

class EntityRepo(ABC, Generic[GenericEntity, GenericEntityId], metaclass=EntityRepoMeta):
    ENTITY_CLS: type[GenericEntity]
    DATA_STORE_TYPE: Enum

    def __init__(self, db_session):
        self.db_session = db_session
        self._tracked_entities: MutableMapping[GenericEntityId, GenericEntity] = {}

    def shutdown(self):
        self.db_session = None
        self._tracked_entities = {}

    @abstractmethod
    def _by_ids(self, ids: Sequence[GenericEntityId], filters: Sequence[NEEDSTYPEHINT]) -> Sequence[GenericEntity]:
            raise NotImplemented

    # def __getattribute__(self, __name: str) -> Any: TODO: (Hristo) raise on uninit repo

    # TODO: (Hristo) add, get, update/save methods, delete ?
    # TODO: (Hristo) Bulkk_update/save, filter on other cols ?
    # TODO: (Hristo) How do we handle caching/ returning same Ent. obj across session, is current too heavy handed
    def get(self, ids: Sequence[GenericEntityId],
            filters: Sequence[NEEDSTYPEHINT]) -> Mapping[GenericEntityId, GenericEntity]:
        entities = {}
        entities_to_retrive = []

        for id in ids:
            if id in self._tracked_entities:
                entities[id] = self._tracked_entities[id]
            else:
                entities_to_retrive.append(id)

        if entities_to_retrive:
            retrieved_entites = self._by_ids(entities_to_retrive, filters)

            for entity in retrieved_entites:
                self._tracked_entities[entity.id] = entity
                entities[entity.id] = entity

        return entities


class EntityRepoManager:
    repo_types = _entity_repo_classes
    session_getters_by_data_source_type = _data_store_session_getters
    # TODO: (Hristo) How do we handle optimistic concurrency
    def __init__(self):
        self.repo_instances = {} # TODO: (Hristo) these should go on a repo session object

    def __getitem__(self, entity_name):
        # TODO:(Hristo) Add exception for missing/ unregistered repo
        repo_type = self.repo_types[entity_name]
        if repo_type in self.repo_instances:
            repo_instance = self.repo_instances[repo_type]
            logger.debug("DB using existing session")
        else:
            session = self.session_getters_by_data_source_type[repo_type.DATA_STORE_TYPE]()
            session.begin()
            repo_instance = repo_type(session)
            logger.debug(f"DB Session start: {session}")
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
                if with_commit:
                    repo.db_session.commit()
                repo.db_session.close()
                logger.debug(f"DB Session end: {repo.db_session}")
                repo.shutdown()

            self.repo_instances = {}

    def update_mutated(self):
        # TODO: (Hristo) How do we handle tracking "dirtied/ mutated" entities, do we want this as part of framework

        pass
