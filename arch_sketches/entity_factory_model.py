from typing import Type
from typing import Optional
from typing import Protocol
from typing import ABC

from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select


# ----------------------------------------------------------------------------------------------------
# Db/Orm Agnostic Repo
# ----------------------------------------------------------------------------------------------------
EntityId = int
DbSession = Session # Union of supported db session types ?!


class Entity:
    id: EntityId
    _mutated: bool
    _version: int

    @staticmethod
    def mutator(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            args[0]._mutated = True
            return res

class EntityFactory(ABC):
    entity_type: Type[BaseModel]

    def coerce_db_to_ent_id(id: int) -> EntityId:
        return id

    def coerce_ent_to_db_ids(ids: list[EntityId]) -> list[int]:
        return ids

    def map_to_entities(self, raw_data) 
        entities = {}
        for raw_data_item in data_models:
            entity = self.entity_type()
            self.map(data_model, entity)
            entities[self.coerce_db_to_ent_id(raw_data_item.id)] = entity
        return entities

    @abstractstaticmethod
    def by_ids(db_session: DbSession, ids: list[EntityId]) -> dict[EntityId, Entity]:
        pass

    @abstractstaticmethod
    def update(db_session: DbSession, entity: Entity):
        pass

class EntityRepoConfig:
    entity_factories: dict[Type[Entity], EntityFactory]

    def __init__():
        self.entity_factories = {}

    def register_entities(self, entity_configs: list[tuple[Type[Entity], EntityFactory]]):
        for ent_cfg in entity_configs:
            self.entity_factories[ent_cfg[0]] = ent_cfg[1]

class EntityRepoSession:
    def __init__(session: DbSession, config: EntityRepoConfig):
        this.config = config
        this.session = session

    def by_ids(ent_type: Type[Entity], ids: list[EntityId]) -> dict[EntityId, Entity]:
        return this.config[ent_type].by_ids(this.session, ids)

    def update(entity: Entity):
        this.config[type(entiry)].update(this.session, entity)

# ----------------------------------------------------------------------------------------------------
# Generic SqlModel setup, might make sense to stick to plain sqlalch and not sqlmodel here
# ----------------------------------------------------------------------------------------------------
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)
    #_version: How do we add sqlalch versioning to these models


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
    hero_4 = Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32)
    hero_5 = Hero(name="Black Lion", secret_name="Trevor Challa", age=35)
    hero_6 = Hero(name="Dr. Weird", secret_name="Steve Weird", age=36)
    hero_7 = Hero(name="Captain North America", secret_name="Esteban Rogelios", age=93)

    with Session(engine) as session:
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.add(hero_4)
        session.add(hero_5)
        session.add(hero_6)
        session.add(hero_7)

        session.commit()


# def update_heroes():
#     with Session(engine) as session:
#         statement = select(Hero).where(Hero.name == "Spider-Boy")  
#         results = session.exec(statement)  
#         hero = results.one()  
#         print("Hero:", hero)  
#
#         hero.age = 16  
#         session.add(hero)  
#         session.commit()  
#         print("Updated hero (without refresh):", hero, type(hero), "END")  
#         print("Updated hero exact prop:", hero.age)  
#         session.refresh(hero)  
#         print("Updated hero:", hero)  

# Domain 
# ----------------------------------------------------------------------------------------------------

@dataclass
class HeroEntity(Entity):
    name: str
    age: int

    @Entity.mutator
    def rebirth_hero(self):
        if age > 50:
            self.age = 0


# ----------------------------------------------------------------------------------------------------
# Repo datalayer
# ----------------------------------------------------------------------------------------------------

class HeroFactory(EntityFactory):
    def map(hero: Hero, hero_ent: HeroEntity):
        hero_ent.name = hero.name
        hero_ent.age = hero.age

    def rev_map(hero_ent: HeroEntity, hero: Hero):
        # Where/how do we move to be part of framework code
        if hero._version != hero_ent._verstio:
            raise
        pass



    @staticmethod
    def by_ids(db_session: DbSession, ids: list[EntityId]) -> dict[EntityId, Entity]:
        #Add joins etc here.
        statement = select(Hero).where(Hero.id in self.coerce_ent_to_db_ids(ids))
        results = session.exec(statement).all()

    return self.map_to_entities(results)


    @staticmethod
    def update(db_session: DbSession, entity: Entity):
        pass

# ----------------------------------------------------------------------------------------------------
repo_config = EntityRepoConfig() 
repo_config.register_entities([(HeroEntity, HeroFactory)])

def get_session():
    with Session(engine) as session:
        yield EntityRepo(session, repo_config)  
        session.commit()

def endpoint_handler(session_injector=get_session):
    with get_session() as repo:
        heros = repo.by_ids(HeroEntity, [0])
        print(heros)
        heros.items()[0].rebirth_hero()


# ----------------------------------------------------------------------------------------------------

def main():
    create_db_and_tables()
    create_heroes()
    # update_heroes()
    endpoint_handler()


if __name__ == "__main__":
    main()

