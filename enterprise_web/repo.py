from typing import Protocol

class EntityRepoType(Protocol):
    pass

# class EntityFactory(Protocol):
#     def by_id(self, id: list[int]) -> 'Entity':
#         ...

def pretend_get_db_data(models):
    data = []
    for model in models:
        data.append(model(name='Some test project name', id='123'))

    return data

class EntityFactory:
    def __init__(self, entity_cls):
        self.entity_cls = entity_cls

    def by_id(self, ids: list[int]) -> list['Entity']:
        entities = []
        for id in ids:
            entity = self.entity_cls()
            # TODO: How do we get model instances from DB
            # TODO: First integration pydantic sql lib. for data retrieval
            populated_models = pretend_get_db_data(self.entity_cls.models)

            entity.data = {}
            for model in populated_models:
                # TODO: What does the naming convention for the populated model key look like?
                entity.data['project'] = model

            entities.append(entity)

        return entities

class EntityRepo:
    # TODO: How do we handle ids, How do we handle commiting and updates, How do we handle caching 
    # TODO: How do we handle optimistic concurrency
    def __init__(self, entity_classes):
        self.repos = {} 
        for entity_class in entity_classes:
            self.repos[entity_class.__name__] = EntityFactory(entity_class)

